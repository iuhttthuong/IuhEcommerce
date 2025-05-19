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
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from env import env
from models.message import CreateMessagePayload
from repositories.message import MessageRepository
from services.products import ProductServices

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
    def __init__(self):
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.agent = self._create_review_agent()
        self.sentiment_model = self._load_or_train_sentiment_model()
        self.vectorizer = self._load_or_create_vectorizer()

    def _create_review_agent(self) -> ConversableAgent:
        system_message = """
        Bạn là Review Analysis & Q&A Agent thông minh cho hệ thống thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. Tóm tắt đánh giá sản phẩm từ người dùng
        2. Phân tích cảm xúc (sentiment) từ các đánh giá
        3. Trả lời câu hỏi dựa trên nội dung đánh giá
        4. Cung cấp thông tin về ưu/nhược điểm sản phẩm từ đánh giá
        
        Mỗi khi nhận được yêu cầu, bạn cần xác định:
        1. Sản phẩm được đề cập (ID hoặc tên)
        2. Loại thông tin người dùng muốn biết về đánh giá
        3. Cách trình bày thông tin phù hợp với yêu cầu
        
        Hãy trả về một JSON với cấu trúc:
        {
            "query_type": "summary | sentiment | specific_question | recommendation",
            "product_identifier": {
                "type": "id | name | category",
                "value": "Giá trị định danh"
            },
            "focus_aspects": ["aspect1", "aspect2"],
            "question": "Câu hỏi cụ thể nếu có"
        }
        """
        return autogen.ConversableAgent(
            name="review_agent",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _load_or_create_vectorizer(self):
        """Load TF-IDF vectorizer from disk or create a new one"""
        vectorizer_path = "models/review_vectorizer.pkl"
        
        if os.path.exists(vectorizer_path):
            try:
                with open(vectorizer_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading vectorizer: {e}")
                
        # Create new vectorizer with mock training data
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Sample reviews for training
        sample_reviews = [
            "Sản phẩm rất tốt, chất lượng cao",
            "Tôi thất vọng với sản phẩm này",
            "Giao hàng nhanh, đóng gói cẩn thận",
            "Sản phẩm không đúng như mô tả",
            "Giá cả hợp lý, đáng đồng tiền",
            "Chất lượng kém, dễ hỏng",
            "Dịch vụ khách hàng tốt",
            "Không hài lòng với sản phẩm",
            "Sản phẩm đẹp, chất lượng tốt",
            "Kém chất lượng, không đáng giá tiền"
        ]
        
        # Fit vectorizer
        vectorizer.fit(sample_reviews)
        
        # Save vectorizer
        os.makedirs("models", exist_ok=True)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
            
        return vectorizer

    def _load_or_train_sentiment_model(self):
        """Load XGBoost sentiment model from disk or train a new one"""
        model_path = "models/sentiment_model.xgb"
        
        # Check if model exists
        if os.path.exists(model_path):
            try:
                return xgb.Booster(model_file=model_path)
            except Exception as e:
                logger.error(f"Error loading XGBoost model: {e}")
        
        # If model doesn't exist or loading failed, train a new one
        logger.info("Training new XGBoost sentiment analysis model")
        
        # Generate synthetic training data
        X_train, y_train = self._generate_synthetic_review_data()
        
        # Train XGBoost model
        dtrain = xgb.DMatrix(X_train, label=y_train)
        param = {
            'max_depth': 3, 
            'eta': 0.1, 
            'objective': 'multi:softmax',
            'num_class': 3,  # Negative (0), Neutral (1), Positive (2)
            'eval_metric': 'mlogloss'
        }
        
        num_rounds = 50
        model = xgb.train(param, dtrain, num_rounds)
        
        # Save model
        os.makedirs("models", exist_ok=True)
        model.save_model(model_path)
        
        return model

    def _generate_synthetic_review_data(self, n_samples=500):
        """Generate synthetic data for training the sentiment analysis model"""
        # Sample positive reviews
        positive_reviews = [
            "Sản phẩm tuyệt vời, chất lượng cao và đáng tiền",
            "Tôi rất hài lòng với sản phẩm này, sẽ mua lại",
            "Giao hàng nhanh, đóng gói cẩn thận, sản phẩm chất lượng",
            "Giá cả hợp lý, sản phẩm đẹp và bền",
            "Chất lượng tốt, đúng như mô tả",
            "Dịch vụ khách hàng tuyệt vời",
            "Sản phẩm đẹp, chất lượng tốt, đáng mua",
            "Rất hài lòng với sản phẩm này",
            "Sẽ giới thiệu cho bạn bè mua",
            "Vượt quá mong đợi của tôi"
        ]
        
        # Sample neutral reviews
        neutral_reviews = [
            "Sản phẩm bình thường, không có gì đặc biệt",
            "Đúng với giá tiền, không quá tốt nhưng cũng không tệ",
            "Giao hàng hơi chậm nhưng sản phẩm ổn",
            "Chất lượng tạm được, cần cải thiện thêm",
            "Sản phẩm đúng như mô tả, không hơn không kém",
            "Có thể dùng được, không quá xuất sắc",
            "Cũng được, nhưng có thể tốt hơn",
            "Trung bình, không có gì nổi bật",
            "Tạm chấp nhận được với mức giá này",
            "Không tệ nhưng cũng không ấn tượng"
        ]
        
        # Sample negative reviews
        negative_reviews = [
            "Sản phẩm kém chất lượng, không đáng tiền",
            "Tôi thất vọng với sản phẩm này",
            "Giao hàng chậm, sản phẩm không như mô tả",
            "Chất lượng kém, dễ hỏng",
            "Không hài lòng với sản phẩm và dịch vụ",
            "Sản phẩm không đúng như hình ảnh",
            "Tôi sẽ không mua lại sản phẩm này",
            "Quá đắt so với chất lượng",
            "Sản phẩm hỏng ngay sau khi mở hộp",
            "Tệ nhất tôi từng mua"
        ]
        
        # Create augmented review data
        reviews = []
        sentiments = []
        
        # For each base review, create variations
        for base_reviews, sentiment in [(positive_reviews, 2), (neutral_reviews, 1), (negative_reviews, 0)]:
            for base in base_reviews:
                # Add original
                reviews.append(base)
                sentiments.append(sentiment)
                
                # Add variations with slight modifications
                for _ in range(n_samples // 30):  # Create enough variations
                    if sentiment == 2:  # Positive
                        prefix = random.choice(["Tuyệt vời! ", "Rất tốt! ", "Xuất sắc! ", "Tôi thích ", ""])
                        suffix = random.choice([" Đề xuất cao!", " Sẽ mua lại!", " Đáng đồng tiền!", ""])
                    elif sentiment == 1:  # Neutral
                        prefix = random.choice(["Tạm được. ", "Bình thường. ", "Tạm chấp nhận. ", ""])
                        suffix = random.choice([" Cần cải thiện.", " Không đặc biệt.", " Giá hơi cao.", ""])
                    else:  # Negative
                        prefix = random.choice(["Kém! ", "Thất vọng! ", "Không tốt! ", "Không nên mua! ", ""])
                        suffix = random.choice([" Không đáng tiền.", " Sẽ không mua lại.", " Chất lượng kém.", ""])
                        
                    variation = prefix + base + suffix
                    reviews.append(variation)
                    sentiments.append(sentiment)
        
        # Vectorize reviews
        X = self.vectorizer.transform(reviews).toarray()
        y = np.array(sentiments)
        
        return X, y

    def _predict_sentiment(self, review_texts):
        """Predict sentiment of review texts using XGBoost model"""
        try:
            # Vectorize review texts
            X = self.vectorizer.transform(review_texts).toarray()
            
            # Make predictions
            dtest = xgb.DMatrix(X)
            predictions = self.sentiment_model.predict(dtest)
            
            # Map numeric predictions to sentiment labels
            sentiment_labels = []
            for pred in predictions:
                if pred == 0:
                    sentiment_labels.append("Tiêu cực")
                elif pred == 1:
                    sentiment_labels.append("Trung lập")
                else:
                    sentiment_labels.append("Tích cực")
                    
            return sentiment_labels
        except Exception as e:
            logger.error(f"Error predicting sentiment: {e}")
            # Return neutral as fallback
            return ["Trung lập"] * len(review_texts)

    def _extract_review_query(self, response: str) -> Dict[str, Any]:
        try:
            # Tìm JSON trong kết quả
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning(f"Không tìm thấy JSON trong phản hồi: {response}")
                return {
                    "query_type": "summary", 
                    "product_identifier": {"type": "id", "value": 0},
                    "focus_aspects": ["general"],
                    "question": ""
                }
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi giải mã JSON: {e}")
            return {
                "query_type": "summary", 
                "product_identifier": {"type": "id", "value": 0},
                "focus_aspects": ["general"],
                "question": ""
            }

    def _find_product_id(self, product_query: Dict[str, Any]) -> Optional[int]:
        try:
            identifier = product_query.get("product_identifier", {})
            id_type = identifier.get("type")
            value = identifier.get("value")
            
            if id_type == "id" and isinstance(value, int):
                # Kiểm tra sản phẩm tồn tại
                product = ProductServices.get(value)
                if product:
                    return value
            elif id_type == "name" and isinstance(value, str):
                # TODO: Implement search by name
                # Mock implementation
                return 101
                
            return None
        except Exception as e:
            logger.error(f"Lỗi khi tìm product ID: {e}")
            return None

    def _get_reviews(self, product_id: int) -> List[Dict[str, Any]]:
        # Mock implementation - in a real system would fetch from database
        # This would connect to your review database
        
        reviews = [
            {
                "review_id": 1,
                "user_id": 123,
                "user_name": "Nguyễn Văn A",
                "rating": 5,
                "title": "Sản phẩm tuyệt vời",
                "content": "Tôi rất hài lòng về sản phẩm này. Chất lượng tốt, giao hàng nhanh, đúng mô tả.",
                "date": "2023-03-15",
                "helpful_votes": 12,
                "verified_purchase": True
            },
            {
                "review_id": 2,
                "user_id": 456,
                "user_name": "Trần Thị B",
                "rating": 4,
                "title": "Sản phẩm khá tốt",
                "content": "Sản phẩm khá ổn với mức giá này. Tuy nhiên, màu sắc không đúng như hình.",
                "date": "2023-03-10",
                "helpful_votes": 5,
                "verified_purchase": True
            },
            {
                "review_id": 3,
                "user_id": 789,
                "user_name": "Lê Văn C",
                "rating": 2,
                "title": "Chất lượng kém",
                "content": "Sản phẩm không đúng như mô tả. Chất liệu kém, dễ hỏng.",
                "date": "2023-02-28",
                "helpful_votes": 8,
                "verified_purchase": True
            },
            {
                "review_id": 4,
                "user_id": 101,
                "user_name": "Phạm Thị D",
                "rating": 5,
                "title": "Đáng đồng tiền",
                "content": "Giá cả hợp lý, chất lượng tốt. Nhân viên giao hàng thân thiện.",
                "date": "2023-02-20",
                "helpful_votes": 3,
                "verified_purchase": False
            },
            {
                "review_id": 5,
                "user_id": 202,
                "user_name": "Hoàng Văn E",
                "rating": 3,
                "title": "Bình thường",
                "content": "Sản phẩm bình thường, không có gì nổi bật. Giao hàng chậm.",
                "date": "2023-02-15",
                "helpful_votes": 1,
                "verified_purchase": True
            },
        ]
        
        # Randomize ratings a bit to make different results per product
        seed = product_id % 10
        random.seed(seed)
        
        for review in reviews:
            random_factor = random.randint(-1, 1)
            review["rating"] = max(1, min(5, review["rating"] + random_factor))
            
        return reviews

    def _analyze_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not reviews:
            return {
                "average_rating": 0,
                "sentiment": "No reviews",
                "positive_percentage": 0,
                "negative_percentage": 0,
                "neutral_percentage": 0,
                "total_reviews": 0
            }
        
        # Extract review contents for ML-based sentiment analysis
        review_texts = [review["content"] for review in reviews]
        
        # Predict sentiment using XGBoost model
        ml_sentiments = self._predict_sentiment(review_texts)
        
        # Count sentiments from ML predictions
        positive_count = ml_sentiments.count("Tích cực")
        negative_count = ml_sentiments.count("Tiêu cực")
        neutral_count = ml_sentiments.count("Trung lập")
        
        # Also use ratings as a secondary signal
        rating_positive = sum(1 for review in reviews if review["rating"] >= 4)
        rating_negative = sum(1 for review in reviews if review["rating"] <= 2)
        rating_neutral = len(reviews) - rating_positive - rating_negative
        
        # Combine both signals (ML and ratings) with higher weight to ML
        positive_count = int(0.7 * positive_count + 0.3 * rating_positive)
        negative_count = int(0.7 * negative_count + 0.3 * rating_negative)
        neutral_count = len(reviews) - positive_count - negative_count
        
        # Calculate average rating
        total_rating = sum(review["rating"] for review in reviews)
        average_rating = total_rating / len(reviews)
        
        # Calculate percentages
        positive_percentage = (positive_count / len(reviews)) * 100
        negative_percentage = (negative_count / len(reviews)) * 100
        neutral_percentage = (neutral_count / len(reviews)) * 100
        
        # Determine overall sentiment
        if positive_percentage > 60:
            sentiment = "Rất tích cực"
        elif positive_percentage > 40:
            sentiment = "Tích cực"
        elif negative_percentage > 60:
            sentiment = "Rất tiêu cực"
        elif negative_percentage > 40:
            sentiment = "Tiêu cực"
        else:
            sentiment = "Trung lập"
            
        # Add per-review sentiment for deeper analysis
        review_sentiments = []
        for i, review in enumerate(reviews):
            review_sentiments.append({
                "review_id": review["review_id"],
                "rating": review["rating"],
                "ml_sentiment": ml_sentiments[i]
            })
            
        return {
            "average_rating": round(average_rating, 1),
            "sentiment": sentiment,
            "positive_percentage": round(positive_percentage, 1),
            "negative_percentage": round(negative_percentage, 1),
            "neutral_percentage": round(neutral_percentage, 1),
            "total_reviews": len(reviews),
            "review_sentiments": review_sentiments
        }

    def _summarize_reviews(self, reviews: List[Dict[str, Any]], focus_aspects: List[str]) -> Dict[str, Any]:
        if not reviews:
            return {
                "summary": "Chưa có đánh giá nào cho sản phẩm này.",
                "pros": [],
                "cons": [],
                "aspects": {}
            }
            
        sentiment_analysis = self._analyze_sentiment(reviews)
        
        # Extract common pros and cons based on ratings and ML sentiment
        pros = []
        cons = []
        
        # Match reviews with their ML sentiment
        review_sentiments = sentiment_analysis.get("review_sentiments", [])
        review_sentiment_map = {rs["review_id"]: rs["ml_sentiment"] for rs in review_sentiments}
        
        # In a real system, this would use NLP to extract common phrases/topics
        # Here we're using a simple approach based on sentiment and content
        for review in reviews:
            review_id = review["review_id"]
            content = review["content"].lower()
            ml_sentiment = review_sentiment_map.get(review_id, "Trung lập")
            
            if ml_sentiment == "Tích cực" or review["rating"] >= 4:
                if "chất lượng tốt" in content or "tuyệt vời" in content:
                    pros.append("Chất lượng tốt")
                if "giao hàng nhanh" in content:
                    pros.append("Giao hàng nhanh")
                if "đúng mô tả" in content:
                    pros.append("Đúng như mô tả")
                if "giá cả hợp lý" in content or "đáng đồng tiền" in content:
                    pros.append("Giá cả hợp lý")
                    
            elif ml_sentiment == "Tiêu cực" or review["rating"] <= 2:
                if "chất lượng kém" in content:
                    cons.append("Chất lượng kém")
                if "không đúng mô tả" in content:
                    cons.append("Không đúng như mô tả")
                if "dễ hỏng" in content:
                    cons.append("Dễ hỏng")
                if "giao hàng chậm" in content:
                    cons.append("Giao hàng chậm")
        
        # Remove duplicates and limit length
        pros = list(set(pros))[:5]
        cons = list(set(cons))[:5]
        
        # Create a simple summary
        if sentiment_analysis["sentiment"] in ["Rất tích cực", "Tích cực"]:
            summary = f"Đa số người dùng hài lòng với sản phẩm này. Điểm đánh giá trung bình là {sentiment_analysis['average_rating']}/5 từ {sentiment_analysis['total_reviews']} đánh giá. Phân tích cảm xúc từ đánh giá cho thấy {sentiment_analysis['positive_percentage']}% ý kiến tích cực."
        elif sentiment_analysis["sentiment"] == "Trung lập":
            summary = f"Đánh giá về sản phẩm này khá trung lập. Điểm đánh giá trung bình là {sentiment_analysis['average_rating']}/5 từ {sentiment_analysis['total_reviews']} đánh giá. Phân tích cảm xúc cho thấy {sentiment_analysis['neutral_percentage']}% ý kiến trung lập."
        else:
            summary = f"Nhiều người dùng không hài lòng với sản phẩm này. Điểm đánh giá trung bình là {sentiment_analysis['average_rating']}/5 từ {sentiment_analysis['total_reviews']} đánh giá. Phân tích cảm xúc cho thấy {sentiment_analysis['negative_percentage']}% ý kiến tiêu cực."
        
        # Create aspect-specific summaries
        # In a real system, this would use NLP to classify review content by aspect
        aspects = {}
        if "general" not in focus_aspects:
            for aspect in focus_aspects:
                if aspect.lower() == "chất lượng" or aspect.lower() == "quality":
                    aspects["Chất lượng"] = "Đa số đánh giá cho rằng chất lượng sản phẩm tốt." if sentiment_analysis["positive_percentage"] > 50 else "Nhiều đánh giá phàn nàn về chất lượng sản phẩm."
                elif aspect.lower() == "giá cả" or aspect.lower() == "price":
                    aspects["Giá cả"] = "Người dùng cho rằng sản phẩm có giá cả hợp lý." if sentiment_analysis["positive_percentage"] > 50 else "Nhiều đánh giá cho rằng sản phẩm không xứng đáng với giá tiền."
                elif aspect.lower() == "giao hàng" or aspect.lower() == "delivery":
                    aspects["Giao hàng"] = "Dịch vụ giao hàng nhanh và đáng tin cậy." if sentiment_analysis["positive_percentage"] > 50 else "Có một số phàn nàn về thời gian giao hàng."
                    
        return {
            "summary": summary,
            "pros": pros,
            "cons": cons,
            "aspects": aspects,
            "sentiment": sentiment_analysis
        }

    def _answer_specific_question(self, reviews: List[Dict[str, Any]], question: str) -> str:
        if not reviews:
            return "Chưa có đánh giá nào cho sản phẩm này, nên tôi không thể trả lời câu hỏi của bạn."
            
        # In a real system, this would use NLP to find reviews relevant to the question
        # and generate an answer based on those reviews
        # Here we're providing some canned responses based on keywords
        
        question_lower = question.lower()
        
        if "chất lượng" in question_lower:
            positive_reviews = [r for r in reviews if r["rating"] >= 4]
            negative_reviews = [r for r in reviews if r["rating"] <= 2]
            
            if len(positive_reviews) > len(negative_reviews):
                return "Dựa trên đánh giá của người dùng, chất lượng sản phẩm này khá tốt. Nhiều người dùng đánh giá cao về độ bền và hoàn thiện của sản phẩm."
            else:
                return "Có một số phàn nàn về chất lượng sản phẩm. Một số người dùng cho rằng sản phẩm không đáng tin cậy và dễ hỏng."
                
        elif "giá" in question_lower or "cả" in question_lower:
            return "Nhiều đánh giá cho rằng sản phẩm có giá cả hợp lý so với các sản phẩm tương tự trên thị trường."
            
        elif "giao hàng" in question_lower or "vận chuyển" in question_lower:
            return "Hầu hết người dùng hài lòng với thời gian giao hàng. Một số đánh giá gần đây cho biết thời gian giao hàng trung bình là 2-3 ngày."
            
        elif "có nên mua" in question_lower or "có đáng mua" in question_lower:
            sentiment = self._analyze_sentiment(reviews)
            if sentiment["average_rating"] >= 4.0:
                return "Dựa trên đánh giá rất tích cực từ người dùng, sản phẩm này rất đáng cân nhắc. Đa số người mua đều hài lòng với quyết định của họ."
            elif sentiment["average_rating"] >= 3.0:
                return "Đánh giá về sản phẩm này khá tốt. Bạn có thể cân nhắc mua sản phẩm này, nhưng nên tìm hiểu kỹ để đảm bảo nó phù hợp với nhu cầu của bạn."
            else:
                return "Đánh giá về sản phẩm này không mấy tích cực. Bạn nên xem xét các sản phẩm thay thế."
        
        # Default response
        return "Dựa trên đánh giá của người dùng, tôi không thể trả lời chính xác câu hỏi của bạn. Hãy xem xét các đánh giá cụ thể để có thông tin chi tiết hơn."

    def _make_recommendation(self, reviews: List[Dict[str, Any]]) -> str:
        if not reviews:
            return "Chưa có đánh giá nào cho sản phẩm này, nên tôi không thể đưa ra khuyến nghị."
            
        sentiment = self._analyze_sentiment(reviews)
        
        if sentiment["average_rating"] >= 4.0:
            return "Dựa trên đánh giá rất tích cực từ người dùng, tôi khuyến nghị bạn nên mua sản phẩm này. Đa số người dùng hài lòng với chất lượng và giá trị mà sản phẩm mang lại."
        elif sentiment["average_rating"] >= 3.0:
            return "Sản phẩm này nhận được đánh giá khá tích cực. Nếu nó đáp ứng nhu cầu của bạn và nằm trong ngân sách, bạn có thể cân nhắc mua sản phẩm này."
        else:
            return "Dựa trên đánh giá không mấy tích cực từ người dùng, tôi không khuyến khích bạn mua sản phẩm này. Hãy xem xét các sản phẩm thay thế có đánh giá tốt hơn."

    def _format_review_response(self, product_id: int, reviews: List[Dict[str, Any]], query_info: Dict[str, Any]) -> Dict[str, Any]:
        query_type = query_info.get("query_type", "summary")
        focus_aspects = query_info.get("focus_aspects", ["general"])
        question = query_info.get("question", "")
        
        # Get product info
        product = ProductServices.get(product_id)
        product_name = product.name if product else f"Sản phẩm #{product_id}"
        
        if query_type == "summary":
            summary = self._summarize_reviews(reviews, focus_aspects)
            
            response_content = f"### Tóm tắt đánh giá cho {product_name}\n\n"
            response_content += f"{summary['summary']}\n\n"
            
            if summary["pros"]:
                response_content += "**Ưu điểm:**\n"
                for pro in summary["pros"]:
                    response_content += f"- {pro}\n"
                response_content += "\n"
                
            if summary["cons"]:
                response_content += "**Nhược điểm:**\n"
                for con in summary["cons"]:
                    response_content += f"- {con}\n"
                response_content += "\n"
                
            if summary["aspects"]:
                response_content += "**Đánh giá theo khía cạnh:**\n"
                for aspect, asp_summary in summary["aspects"].items():
                    response_content += f"- {aspect}: {asp_summary}\n"
                    
            return {
                "content": response_content,
                "product_id": product_id,
                "review_summary": summary,
                "query_type": "summary"
            }
            
        elif query_type == "sentiment":
            sentiment = self._analyze_sentiment(reviews)
            
            response_content = f"### Phân tích cảm xúc đánh giá cho {product_name}\n\n"
            response_content += f"**Cảm xúc chung:** {sentiment['sentiment']}\n"
            response_content += f"**Điểm đánh giá trung bình:** {sentiment['average_rating']}/5 sao\n"
            response_content += f"**Tổng số đánh giá:** {sentiment['total_reviews']}\n\n"
            response_content += f"**Đánh giá tích cực:** {sentiment['positive_percentage']}%\n"
            response_content += f"**Đánh giá trung lập:** {sentiment['neutral_percentage']}%\n"
            response_content += f"**Đánh giá tiêu cực:** {sentiment['negative_percentage']}%\n"
            
            return {
                "content": response_content,
                "product_id": product_id,
                "review_summary": {"sentiment": sentiment},
                "query_type": "sentiment"
            }
            
        elif query_type == "specific_question":
            answer = self._answer_specific_question(reviews, question)
            
            response_content = f"### Trả lời cho {product_name}\n\n"
            response_content += f"**Câu hỏi:** {question}\n\n"
            response_content += f"**Trả lời:** {answer}\n"
            
            return {
                "content": response_content,
                "product_id": product_id,
                "review_summary": None,
                "query_type": "specific_question"
            }
            
        elif query_type == "recommendation":
            recommendation = self._make_recommendation(reviews)
            
            response_content = f"### Khuyến nghị cho {product_name}\n\n"
            response_content += recommendation
            
            return {
                "content": response_content,
                "product_id": product_id,
                "review_summary": None,
                "query_type": "recommendation"
            }
            
        return {
            "content": f"Không thể xử lý yêu cầu về đánh giá cho {product_name}. Vui lòng thử lại với loại yêu cầu khác.",
            "product_id": product_id,
            "review_summary": None,
            "query_type": "error"
        }

    async def process_request(self, request: ReviewRequest) -> ReviewResponse:
        try:
            # Phân tích yêu cầu
            prompt = f"""
            Hãy phân tích yêu cầu về đánh giá sản phẩm sau:
            "{request.message}"
            
            Các thực thể đã được xác định:
            {request.entities if request.entities else 'Không có thông tin thực thể.'}
            
            Product ID đã được cung cấp: {request.product_id if request.product_id else 'Không có'}
            """
            
            # Gọi agent để phân tích
            agent_response = await self.agent.a_generate_reply(messages=[{"role": "user", "content": prompt}])
            
            # Trích xuất thông tin truy vấn
            query_info = self._extract_review_query(agent_response)
            
            # Nếu đã có product_id từ request, sử dụng nó
            product_id = request.product_id
            if not product_id:
                product_id = self._find_product_id(query_info)
                
            if not product_id:
                return ReviewResponse(
                    content="Xin lỗi, tôi không thể xác định sản phẩm bạn đang hỏi. Vui lòng cung cấp tên sản phẩm hoặc ID cụ thể.",
                    product_id=None,
                    review_summary=None,
                    query_type="error"
                )
                
            # Lấy đánh giá
            reviews = self._get_reviews(product_id)
            
            # Xử lý và định dạng phản hồi
            response_data = self._format_review_response(product_id, reviews, query_info)
            
            # Lưu thông tin tương tác vào message repository
            message_repository = MessageRepository()
            response_payload = CreateMessagePayload(
                chat_id=request.chat_id,
                role="assistant",
                content=response_data["content"],
                metadata={
                    "query_type": response_data["query_type"],
                    "product_id": product_id
                }
            )
            message_repository.create(response_payload)
            
            return ReviewResponse(
                content=response_data["content"],
                product_id=response_data["product_id"],
                review_summary=response_data["review_summary"],
                query_type=response_data["query_type"]
            )
            
        except Exception as e:
            logger.error(f"Lỗi trong review_agent: {e}")
            return ReviewResponse(
                content=f"Đã xảy ra lỗi khi xử lý yêu cầu về đánh giá sản phẩm: {str(e)}",
                product_id=None,
                review_summary=None,
                query_type="error"
            )

@router.post("/analyze", response_model=ReviewResponse)
async def analyze_reviews(request: ReviewRequest):
    try:
        agent = ReviewAgent()
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong analyze_reviews endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}") 