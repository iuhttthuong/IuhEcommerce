import json
from typing import Any, Dict, List, Optional, Union
import random
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from env import env
from models.chats import ChatMessageCreate
from repositories.message import MessageRepository
from services.products import ProductServices
from db import get_db
from models.reviews import Review
from repositories.reviews import ReviewRepositories
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import joblib

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class ReviewRequest(BaseModel):
    chat_id: int
    message: str
    product_id: Optional[int] = None
    entities: Optional[Dict[str, Any]] = None

class ReviewResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    product_id: Optional[int] = Field(default=None, description="ID sản phẩm")
    review_summary: Optional[Dict[str, Any]] = Field(default=None, description="Tóm tắt đánh giá")
    query_type: str = Field(..., description="Loại truy vấn: summary, sentiment, specific_question, recommendation")
    
class ReviewAgent:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepositories(db)
        self.vectorizer = None
        self.model = None
        self._load_or_train_sentiment_model()

    def _load_or_train_sentiment_model(self):
        model_path = "models/sentiment_model.joblib"
        vectorizer_path = "models/vectorizer.joblib"
        
        # Try to load existing model and vectorizer
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info("Loaded existing sentiment analysis model")
                return
            except Exception as e:
                logger.warning(f"Error loading existing model: {str(e)}")

        # Train new model if loading fails
        logger.info("Training new sentiment analysis model")
        reviews = self.review_repo.get_all()
        
        if not reviews:
            logger.warning("No reviews found for training. Using rule-based sentiment analysis.")
            self.model = None
            self.vectorizer = None
            return

        # Prepare data
        df = pd.DataFrame([{
            'text': review.comment,
            'sentiment': 1 if review.rating >= 4 else (0 if review.rating <= 2 else 0.5)
        } for review in reviews])

        # Initialize and fit vectorizer
        self.vectorizer = TfidfVectorizer(max_features=5000)
        X = self.vectorizer.fit_transform(df['text'])
        y = df['sentiment']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        self.model = XGBClassifier()
        self.model.fit(X_train, y_train)

        # Save model and vectorizer
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)
        logger.info("Trained and saved new sentiment analysis model")

    def analyze_sentiment(self, text: str) -> float:
        if not self.vectorizer or not self.model:
            # Simple rule-based sentiment analysis as fallback
            positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect', 'wonderful', 'fantastic', 'awesome'}
            negative_words = {'bad', 'poor', 'terrible', 'awful', 'worst', 'hate', 'disappointing', 'useless', 'waste', 'horrible'}
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total = positive_count + negative_count
            if total == 0:
                return 0.5  # Neutral if no sentiment words found
            
            return positive_count / total
        
        # Transform text
        X = self.vectorizer.transform([text])
        
        # Predict sentiment
        sentiment = self.model.predict_proba(X)[0]
        return float(sentiment[1])  # Return positive sentiment probability

    def get_product_sentiment(self, product_id: int) -> dict:
        reviews = self.review_repo.get_by_product(product_id)
        if not reviews:
            return {
                "average_rating": 0,
                "sentiment_score": 0,
                "total_reviews": 0,
                "message": "No reviews available for this product"
            }

        # Calculate metrics
        total_reviews = len(reviews)
        average_rating = sum(review.rating for review in reviews) / total_reviews
        
        # Analyze sentiment for each review
        sentiments = []
        for review in reviews:
            try:
                sentiment = self.analyze_sentiment(review.comment)
                sentiments.append(sentiment)
            except Exception as e:
                logger.error(f"Error analyzing sentiment for review {review.review_id}: {str(e)}")
                continue

        sentiment_score = sum(sentiments) / len(sentiments) if sentiments else 0

        return {
            "average_rating": round(average_rating, 2),
            "sentiment_score": round(sentiment_score, 2),
            "total_reviews": total_reviews,
            "message": "Analysis complete"
        }

    async def process_request(self, request: ReviewRequest) -> ReviewResponse:
        try:
            if request.product_id:
                sentiment_data = self.get_product_sentiment(request.product_id)
                return ReviewResponse(
                    content=f"Product analysis: {sentiment_data['message']}\n"
                           f"Average rating: {sentiment_data['average_rating']}\n"
                           f"Sentiment score: {sentiment_data['sentiment_score']}\n"
                           f"Total reviews: {sentiment_data['total_reviews']}",
                    product_id=request.product_id,
                    review_summary=sentiment_data,
                    query_type="summary"
                )
            else:
                sentiment = self.analyze_sentiment(request.message)
                return ReviewResponse(
                    content=f"Text sentiment analysis: {round(sentiment, 2)}",
                    query_type="sentiment"
                )
        except Exception as e:
            logger.error(f"Unexpected error in process_request: {str(e)}")
            return ReviewResponse(
                content=f"An error occurred while processing your request: {str(e)}",
                query_type="error"
            )

@router.get("/analyze/{product_id}")
def analyze_reviews(product_id: int, db: Session = Depends(get_db)):
    try:
        agent = ReviewAgent(db)
        return agent.get_product_sentiment(product_id)
    except Exception as e:
        logger.error(f"Error in analyze_reviews endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment")
def analyze_text_sentiment(text: str, db: Session = Depends(get_db)):
    try:
        agent = ReviewAgent(db)
        sentiment = agent.analyze_sentiment(text)
        return {"sentiment_score": round(sentiment, 2)}
    except Exception as e:
        logger.error(f"Error in analyze_text_sentiment endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=ReviewResponse)
async def analyze_reviews(request: ReviewRequest, db: Session = Depends(get_db)):
    try:
        agent = ReviewAgent(db)
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong analyze_reviews endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}") 