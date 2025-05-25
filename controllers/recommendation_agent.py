import json
import random
import numpy as np
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pickle
import os
from datetime import datetime

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from env import env
from models.chats import ChatMessageCreate
from repositories.message import MessageRepository
from services.products import ProductServices
from services.search import SearchServices
from embedding.main import COLLECTIONS

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])

class RecommendationRequest(BaseModel):
    chat_id: int
    user_id: Optional[int] = None
    message: str
    context: Optional[Dict[str, Any]] = None  # Ngữ cảnh hiện tại (sản phẩm đang xem, giỏ hàng, v.v.)
    user_profile: Optional[Dict[str, Any]] = None  # Thông tin hồ sơ người dùng (nếu có)

class RecommendationResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Danh sách sản phẩm gợi ý")
    recommendation_type: str = Field(..., description="Loại gợi ý: personalized, contextual, trending, similar")
    context_used: Dict[str, Any] = Field(default_factory=dict, description="Ngữ cảnh được sử dụng để đề xuất")

class RecommendationAgent:
    def __init__(self):
        """Initialize the Recommendation Agent with necessary configurations and models."""
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.agent = self._create_recommendation_agent()
        self.features = ["user_cat_pref", "price_range_min", "price_range_max", "brand_pref", 
                         "total_purchases", "avg_purchase_value", "days_since_last_purchase", 
                         "product_category", "product_price", "product_brand", "product_rating"]
        
        # Initialize services
        self.search_service = SearchServices()
        
        # Initialize encoders first
        self.category_encoder = self._load_or_create_encoder("category")
        self.brand_encoder = self._load_or_create_encoder("brand")
        
        # Then load or train ML model
        self.xgb_model = self._load_or_train_model()
        
        # Define default context for recommendation
        self.default_context = {
            "recent_views": [],
            "recent_searches": [],
            "cart_items": [],
            "purchase_history": []
        }

    def _create_recommendation_agent(self) -> ConversableAgent:
        """Create and return a recommendation agent with appropriate system message."""
        system_message = """
        Bạn là Recommendation Agent thông minh cho hệ thống thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. Phân tích hồ sơ người dùng và ngữ cảnh hiện tại
        2. Đưa ra gợi ý sản phẩm cá nhân hóa
        3. Giải thích lý do đằng sau các gợi ý
        4. Cung cấp các gợi ý phù hợp với ngữ cảnh cuộc trò chuyện
        
        Các loại gợi ý:
        - Personalized: Dựa trên thông tin người dùng, sở thích và lịch sử
        - Contextual: Dựa trên ngữ cảnh hiện tại (sản phẩm đang xem, giỏ hàng)
        - Trending: Sản phẩm phổ biến, bán chạy, mới
        - Similar: Sản phẩm tương tự với sản phẩm đã được quan tâm
        
        Hãy trả về một JSON với cấu trúc:
        {
            "recommendation_type": "personalized | contextual | trending | similar",
            "query_strategy": {
                "approach": "category_based | keyword_based | popularity_based | collaborative | ml_based",
                "query": "Từ khóa hoặc danh mục cần tìm",
                "filters": {
                    "category": "Danh mục (nếu có)",
                    "price_range": {"min": 100000, "max": 5000000}
                }
            },
            "explanation": "Giải thích ngắn gọn về cách gợi ý được tạo ra"
        }
        """
        return autogen.ConversableAgent(
            name="recommendation_agent",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_recommendation_query(self, response: str) -> Dict[str, Any]:
        """Extract JSON recommendation query from agent response with error handling."""
        try:
            # Tìm JSON trong kết quả
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            # Default query if JSON extraction fails
            default_query = {
                "recommendation_type": "trending", 
                "query_strategy": {
                    "approach": "popularity_based", 
                    "query": ""
                }, 
                "explanation": "Gợi ý sản phẩm phổ biến"
            }
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                query = json.loads(json_str)
                
                # Validate essential fields
                if not query.get("recommendation_type") or not query.get("query_strategy"):
                    logger.warning("Thiếu trường bắt buộc trong JSON query")
                    return default_query
                    
                return query
            else:
                logger.warning(f"Không tìm thấy JSON trong phản hồi: {response}")
                return default_query
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi giải mã JSON: {e}")
            return default_query

    def _load_or_create_encoder(self, encoder_type: str):
        """Load encoder from disk or create a new one if not found."""
        encoder_path = f"models/{encoder_type}_encoder.pkl"
        
        if os.path.exists(encoder_path):
            try:
                with open(encoder_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading {encoder_type} encoder: {e}")
                
        # Create new encoder
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        
        # Initialize with sample data based on encoder type
        if encoder_type == "category":
            # Sample categories
            categories = ["electronics", "fashion", "home", "beauty", "sports", "books"]
            encoder.fit(pd.DataFrame(categories, columns=['category']))
        elif encoder_type == "brand":
            # Sample brands
            brands = ["Apple", "Samsung", "Sony", "LG", "Dell", "Nike", "Adidas"]
            encoder.fit(pd.DataFrame(brands, columns=['brand']))
            
        # Save encoder
        os.makedirs("models", exist_ok=True)
        with open(encoder_path, 'wb') as f:
            pickle.dump(encoder, f)
            
        return encoder

    def _load_or_train_model(self):
        """Load XGBoost model from disk or train a new one if not found."""
        model_path = "models/recommendation_model.xgb"
        
        # Check if model exists
        if os.path.exists(model_path):
            try:
                return xgb.Booster(model_file=model_path)
            except Exception as e:
                logger.error(f"Error loading XGBoost model: {e}")
        
        # If model doesn't exist or loading failed, train a new one
        logger.info("Training new XGBoost recommendation model")
        
        try:
            # Generate synthetic training data
            X_train, y_train = self._generate_synthetic_training_data()
            
            if X_train.size == 0 or len(X_train.shape) != 2:
                logger.error("Invalid training data shape")
                return None
                
            # Train XGBoost model with optimized parameters
            dtrain = xgb.DMatrix(X_train, label=y_train)
            
            # Define model parameters
            param = {
                'max_depth': 6,  # Increased depth for better feature interactions
                'eta': 0.1,
                'objective': 'binary:logistic',
                'eval_metric': ['logloss', 'auc'],  # Multiple metrics for better evaluation
                'subsample': 0.8,  # Random subsampling to prevent overfitting
                'colsample_bytree': 0.8,  # Random column sampling
                'min_child_weight': 1,  # Minimum sum of instance weight needed in a child
                'gamma': 0.1,  # Minimum loss reduction required for a split
                'lambda': 1,  # L2 regularization
                'alpha': 0,  # L1 regularization
                'tree_method': 'hist',  # Use histogram-based algorithm for faster training
                'grow_policy': 'lossguide',  # Grow tree based on loss reduction
                'max_leaves': 64,  # Maximum number of leaves in a tree
                'max_bin': 256  # Maximum number of bins for histogram
            }
            
            # Train with early stopping
            num_rounds = 1000
            evals = [(dtrain, 'train')]
            model = xgb.train(
                param,
                dtrain,
                num_rounds,
                evals=evals,
                early_stopping_rounds=50,
                verbose_eval=10
            )
            
            # Save model
            os.makedirs("models", exist_ok=True)
            model.save_model(model_path)
            
            # Save feature importance
            importance = model.get_score(importance_type='gain')
            importance_path = "models/feature_importance.json"
            with open(importance_path, 'w') as f:
                json.dump(importance, f, indent=2)
            
            logger.info(f"Model saved with {model.best_ntree_limit} trees")
            return model
            
        except Exception as e:
            logger.error(f"Error training XGBoost model: {e}")
            return None

    def _generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic data for training the recommendation model."""
        np.random.seed(42)
        
        # Generate user features
        user_cat_pref = np.random.choice(['electronics', 'fashion', 'home', 'beauty', 'sports', 'books'], n_samples)
        price_range_min = np.random.randint(50000, 5000000, n_samples)
        price_range_max = price_range_min + np.random.randint(500000, 5000000, n_samples)
        brand_pref = np.random.choice(['Apple', 'Samsung', 'Sony', 'LG', 'Dell', 'Nike', 'Adidas'], n_samples)
        total_purchases = np.random.randint(0, 50, n_samples)
        avg_purchase_value = np.random.randint(100000, 10000000, n_samples)
        days_since_last_purchase = np.random.randint(1, 365, n_samples)
        
        # Generate product features
        product_category = np.random.choice(['electronics', 'fashion', 'home', 'beauty', 'sports', 'books'], n_samples)
        product_price = np.random.randint(50000, 10000000, n_samples)
        product_brand = np.random.choice(['Apple', 'Samsung', 'Sony', 'LG', 'Dell', 'Nike', 'Adidas'], n_samples)
        product_rating = np.random.uniform(1, 5, n_samples)
        
        # Create features DataFrame
        features = pd.DataFrame({
            'user_cat_pref': user_cat_pref,
            'price_range_min': price_range_min,
            'price_range_max': price_range_max,
            'brand_pref': brand_pref,
            'total_purchases': total_purchases,
            'avg_purchase_value': avg_purchase_value,
            'days_since_last_purchase': days_since_last_purchase,
            'product_category': product_category,
            'product_price': product_price,
            'product_brand': product_brand,
            'product_rating': product_rating
        })
        
        # Process features for training
        features_processed = self._process_features(features)
        
        # Generate target variable based on preference matching logic
        y = []
        for i in range(n_samples):
            score = 0
            # Category match
            if features['user_cat_pref'][i] == features['product_category'][i]:
                score += 0.4
            # Price range match
            if features['price_range_min'][i] <= features['product_price'][i] <= features['price_range_max'][i]:
                score += 0.3
            # Brand preference match
            if features['brand_pref'][i] == features['product_brand'][i]:
                score += 0.2
            # Recent purchase activity
            if features['days_since_last_purchase'][i] < 30:
                score += 0.1
            # High product rating
            if features['product_rating'][i] >= 4.0:
                score += 0.2
                
            # Add randomness for realistic data
            score += np.random.uniform(-0.3, 0.3)
            
            # Convert to binary outcome
            y.append(1 if score >= 0.5 else 0)
        
        return features_processed, np.array(y)

    def _process_features(self, features_df):
        """Process and encode features for model training or prediction."""
        try:
            df = features_df.copy()
            
            # One-hot encode categorical features
            if self.category_encoder and 'user_cat_pref' in df.columns:
                # Create a new DataFrame with consistent column order
                new_df = pd.DataFrame()
                new_df['category'] = df['user_cat_pref']
                cat_encoded = self.category_encoder.transform(new_df[['category']])
                
                # Create column names for the encoded features
                cat_cols = [f'cat_{i}' for i in range(cat_encoded.shape[1])]
                
                # Add encoded features to dataframe
                for i, col in enumerate(cat_cols):
                    df[col] = cat_encoded[:, i]
                
                # Drop original categorical columns
                df = df.drop(['user_cat_pref', 'product_category'], axis=1)
            
            # One-hot encode brand features
            if self.brand_encoder and 'brand_pref' in df.columns:
                # Create a new DataFrame with consistent column order
                new_df = pd.DataFrame()
                new_df['brand'] = df['brand_pref']
                brand_encoded = self.brand_encoder.transform(new_df[['brand']])
                
                # Create column names for the encoded features
                brand_cols = [f'brand_{i}' for i in range(brand_encoded.shape[1])]
                
                # Add encoded features to dataframe
                for i, col in enumerate(brand_cols):
                    df[col] = brand_encoded[:, i]
                
                # Drop original categorical columns
                df = df.drop(['brand_pref', 'product_brand'], axis=1)
            
            # Scale numerical features
            scaler = StandardScaler()
            numerical_cols = ['price_range_min', 'price_range_max', 'total_purchases', 
                            'avg_purchase_value', 'days_since_last_purchase',
                            'product_price', 'product_rating']
            
            numerical_cols = [col for col in numerical_cols if col in df.columns]
            
            if numerical_cols:
                df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            
            # Add interaction features
            if 'product_price' in df.columns and 'price_range_min' in df.columns:
                df['price_affordability'] = (df['price_range_max'] - df['product_price']) / (df['price_range_max'] - df['price_range_min'])
            
            if 'product_rating' in df.columns and 'days_since_last_purchase' in df.columns:
                df['recency_rating'] = df['product_rating'] * (1 / (1 + df['days_since_last_purchase'] / 365))
            
            return df.values
            
        except Exception as e:
            logger.error(f"Error processing features: {e}")
            # Return empty array if processing fails
            return np.array([])

    def _prepare_user_product_features(self, user_profile, product):
        """Prepare features for a specific user-product pair for model prediction."""
        try:
            # Extract user features
            user_cat_pref = user_profile.get('preferred_category', 'electronics')
            price_range_min = user_profile.get('price_min', 100000)
            price_range_max = user_profile.get('price_max', 5000000)
            brand_pref = user_profile.get('preferred_brand', 'Apple')
            total_purchases = user_profile.get('total_purchases', 0)
            avg_purchase_value = user_profile.get('avg_purchase_value', 500000)
            days_since_last_purchase = user_profile.get('days_since_last_purchase', 30)
            
            # Extract product features
            product_category = product.get('category', 'electronics')
            product_price = product.get('price', 1000000)
            product_brand = product.get('brand', 'Apple')
            product_rating = product.get('rating', 4.0)
            
            # Create a single row DataFrame
            features = pd.DataFrame({
                'user_cat_pref': [user_cat_pref],
                'price_range_min': [price_range_min],
                'price_range_max': [price_range_max],
                'brand_pref': [brand_pref],
                'total_purchases': [total_purchases],
                'avg_purchase_value': [avg_purchase_value],
                'days_since_last_purchase': [days_since_last_purchase],
                'product_category': [product_category],
                'product_price': [product_price],
                'product_brand': [product_brand],
                'product_rating': [product_rating]
            })
            
            # Process the features
            processed_features = self._process_features(features)
            return processed_features
        
        except Exception as e:
            logger.error(f"Error preparing user-product features: {e}")
            return None

    def _predict_user_interest(self, user_profile, products):
        """Predict user interest in a list of products using the trained model."""
        if not self.xgb_model or not products:
            return []
            
        try:
            # Prepare feature matrix for all products
            features_list = []
            for product in products:
                # Prepare features for this user-product pair
                features = self._prepare_user_product_features(user_profile, product)
                if features is not None and features.size > 0:
                    features_list.append(features[0])  # First row of the processed features
            
            if not features_list:
                return []
                
            # Convert to numpy array
            X = np.array(features_list)
            
            # Make predictions with probability estimates
            dtest = xgb.DMatrix(X)
            predictions = self.xgb_model.predict(dtest)
            
            # Sort products by prediction score
            product_scores = list(zip(products, predictions))
            sorted_products = sorted(product_scores, key=lambda x: x[1], reverse=True)
            
            # Return products with their scores and probabilities
            return [(product, float(score)) for product, score in sorted_products]
            
        except Exception as e:
            logger.error(f"Error predicting user interest: {e}")
            return []

    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile from User Profile Agent or use defaults."""
        # TODO: Integrate with User Profile Agent when available
        try:
            # For now we use mock data
            mock_profile = {
                "user_id": user_id,
                "preferred_category": random.choice(['electronics', 'fashion', 'home', 'beauty']),
                "preferred_brand": random.choice(['Apple', 'Samsung', 'Sony', 'Nike']),
                "price_min": random.randint(100000, 1000000),
                "price_max": random.randint(1000000, 10000000),
                "total_purchases": random.randint(0, 20),
                "avg_purchase_value": random.randint(200000, 5000000),
                "days_since_last_purchase": random.randint(1, 90),
                "interests": ["technology", "smart home", "gaming"] if random.random() > 0.5 else ["fashion", "beauty", "lifestyle"]
            }
            
            return mock_profile
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            # Return default profile in case of error
            return {
                "user_id": user_id,
                "preferred_category": "electronics",
                "preferred_brand": "Apple",
                "price_min": 100000,
                "price_max": 5000000,
                "total_purchases": 0,
                "avg_purchase_value": 500000,
                "days_since_last_purchase": 30,
                "interests": ["technology"]
            }

    def _find_similar_products(self, product_id: int, limit: int = 5) -> List[Dict]:
        """Find similar products based on product ID."""
        try:
            if not product_id:
                logger.warning("Invalid product ID: None")
                return []
                
            # Get product details
            product_info = ProductServices.get_info(product_id)
            if not product_info or not product_info.get("product"):
                logger.warning(f"Product {product_id} not found")
                return []
                
            product = product_info["product"]
            
            # Search for similar products
            similar_products = self.search_service.search(
                payload=f"{product.name} {product.description}",
                collection_name=COLLECTIONS["products"],
                limit=limit + 1  # Get one extra to exclude original
            )
            
            # Filter out the original product
            similar_products = [p for p in similar_products if p["id"] != product_id]
            
            return similar_products[:limit]  # Return only requested number
            
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            return []

    def _find_category_by_text(self, text: str) -> Optional[int]:
        """Find category ID by searching in category_embeddings collection."""
        try:
            # Search in category_embeddings collection
            search_results = self.search_service.search(
                query=text,
                collection_name="category_embeddings",  # Use direct string instead of COLLECTIONS
                limit=1
            )
            
            if search_results and len(search_results) > 0:
                # Return the category ID from the first result
                return search_results[0].get("id")
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding category by text: {e}")
            return None

    def _find_products_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Find products by category."""
        try:
            if not category:
                logger.warning("Invalid category: None or empty")
                return []
            
            # Find category ID using category_embeddings
            category_id = self._find_category_by_text(category)
            
            if not category_id:
                logger.warning(f"Category not found: {category}")
                return []
                
            # Search by category ID
            search_results = self.search_service.search(
                query=str(category_id),
                collection_name=COLLECTIONS["products"],
                limit=limit
            )
            
            if not search_results:
                logger.warning(f"No products found in category ID: {category_id}")
                return []
                
            return search_results
            
        except Exception as e:
            logger.error(f"Error finding products by category: {e}")
            return []

    def _find_products_by_text(self, text: str, limit: int = 5, category: str = None) -> List[Dict]:
        """Find products by text search."""
        try:
            if not text:
                logger.warning("Invalid search text: None or empty")
                return []
            
            # Get category ID if category is provided
            category_id = None
            if category:
                category_id = self._find_category_by_text(category)
                
            # Search for products
            search_results = self.search_service.search(
                query=text,
                collection_name=COLLECTIONS["products"],
                limit=limit
            )
            
            if not search_results:
                logger.warning(f"No products found for text: {text}")
                return []
                
            return search_results
            
        except Exception as e:
            logger.error(f"Error in _find_products_by_text: {e}")
            return []

    def _find_popular_products(self, limit: int = 5, category: str = None) -> List[Dict]:
        """Find popular products based on ratings and sales."""
        try:
            # Get category ID if category is provided
            category_id = None
            if category:
                category_id = self._find_category_by_text(category)
            
            # Search for popular products
            search_results = self.search_service.search(
                query="popular best selling",
                collection_name=COLLECTIONS["products"],
                limit=limit
            )
            
            if not search_results:
                logger.warning("No popular products found")
                return []
                
            return search_results
            
        except Exception as e:
            logger.error(f"Error finding popular products: {e}")
            return []

    def _execute_recommendation_strategy(self, recommendation_info: Dict[str, Any], user_profile: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute recommendation strategy based on user query analysis."""
        try:
            recommendation_type = recommendation_info.get("recommendation_type", "trending")
            query_strategy = recommendation_info.get("query_strategy", {})
            approach = query_strategy.get("approach", "popularity_based")
            query = query_strategy.get("query", "")
            filters = query_strategy.get("filters", {})
            
            # Apply filters if provided
            limit = 5  # Default limit
            category = filters.get("category")
            
            # Different recommendation strategies
            if recommendation_type == "similar" and query.isdigit():
                # Find similar products to a specific product
                product_id = int(query)
                return self._find_similar_products(product_id, limit)
                
            elif recommendation_type == "personalized":
                if approach == "ml_based" and self.xgb_model:
                    # Use machine learning model for personalized recommendations
                    # First get candidate products
                    if category:
                        candidates = self._find_products_by_category(category, limit=20)
                    else:
                        # Get products based on user's preferred category
                        preferred_category = user_profile.get("preferred_category", "electronics")
                        candidates = self._find_products_by_category(preferred_category, limit=20)
                        
                    # If no candidates found, get popular products
                    if not candidates:
                        candidates = self._find_popular_products(limit=20)
                        
                    # Predict user interest in candidates
                    scored_products = self._predict_user_interest(user_profile, candidates)
                    
                    # Return top recommendations
                    return [product for product, score in scored_products[:limit]]
                else:
                    # Fallback to category-based recommendation
                    preferred_category = user_profile.get("preferred_category", "electronics")
                    return self._find_products_by_category(preferred_category, limit)
                    
            elif recommendation_type == "contextual":
                if context and "recent_views" in context and context["recent_views"]:
                    # Recommend based on recently viewed product
                    recent_product_id = context["recent_views"][0]
                    return self._find_similar_products(recent_product_id, limit)
                elif query:
                    # Use the query text to find products
                    return self._find_products_by_text(query, limit, category)
                else:
                    # Fallback to popular products
                    return self._find_popular_products(limit)
                    
            elif approach == "category_based" and category:
                # Category-based recommendation
                return self._find_products_by_category(category, limit)
                
            elif approach == "keyword_based" and query:
                # Keyword-based recommendation
                return self._find_products_by_text(query, limit, category)
            
            else:
                # Default: popularity-based recommendation
                return self._find_popular_products(limit)
                
        except Exception as e:
            logger.error(f"Error executing recommendation strategy: {e}")
            # Fallback to popular products in case of error
            return self._find_popular_products(5)

    def _generate_response(self, recommendations: List[Dict[str, Any]], recommendation_info: Dict[str, Any]) -> str:
        """Generate a human-friendly response with recommendations."""
        try:
            recommendation_type = recommendation_info.get("recommendation_type", "trending")
            explanation = recommendation_info.get("explanation", "")
            
            if not recommendations:
                return "Xin lỗi, tôi không tìm thấy sản phẩm phù hợp với yêu cầu của bạn."
                
            # Start with a context-appropriate introduction
            if recommendation_type == "personalized":
                response = "Dựa trên sở thích và lịch sử mua hàng của bạn, tôi gợi ý những sản phẩm sau:\n\n"
            elif recommendation_type == "contextual":
                response = "Dựa trên ngữ cảnh hiện tại, tôi nghĩ bạn có thể quan tâm đến:\n\n"
            elif recommendation_type == "similar":
                response = "Đây là một số sản phẩm tương tự mà bạn có thể thích:\n\n"
            else:  # trending
                response = "Đây là những sản phẩm đang được ưa chuộng:\n\n"
                
            # Add product details
            for i, product in enumerate(recommendations[:5], 1):
                product_data = product.get('payload', {})
                name = product_data.get('name', 'Sản phẩm không tên')
                price = product_data.get('price', 0)
                rating = product_data.get('rating_average', 0)
                short_description = product_data.get('short_description', '')
                
                # Format description to keep it short
                if short_description:
                    short_description = short_description[:100] + "..." if len(short_description) > 100 else short_description
                
                response += f"{i}. **{name}** - {price:,} VND"
                if rating:
                    response += f" (⭐ {rating})"
                response += "\n"
                if short_description:
                    response += f"   {short_description}\n"
                response += "\n"
                
            # Add explanation if available
            if explanation:
                response += f"\n{explanation}\n"
                
            # Add a call to action
            response += "\nBạn có thể nhấp vào bất kỳ sản phẩm nào để xem chi tiết hoặc cho tôi biết nếu bạn muốn xem thêm sản phẩm khác."
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            product_names = ", ".join([p.get('payload', {}).get('name', 'Sản phẩm') for p in recommendations[:3]])
            return f"Tôi đã tìm thấy một số sản phẩm có thể phù hợp với bạn: {product_names}."

    async def process_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Process recommendation request and return personalized recommendations."""
        try:
            # Use provided user profile or fetch it
            user_profile = getattr(request, 'user_profile', None)
            if not user_profile and request.user_id:
                user_profile = await self._get_user_profile(request.user_id)
            elif not user_profile:
                # Create default user profile if none provided
                user_profile = {
                    "preferred_category": "beauty",  # Default to beauty for lipstick
                    "preferred_brand": "Maybelline",  # Default to popular makeup brand
                    "price_min": 50000,  # Lower price range for affordable lipstick
                    "price_max": 200000  # Upper limit for affordable lipstick
                }
                
            # Use provided context or create default
            context = request.context or self.default_context
                
            # Analyze message with LLM to determine recommendation strategy
            prompt = f"""
            Phân tích yêu cầu của người dùng và đề xuất chiến lược gợi ý sản phẩm phù hợp.
            
            Người dùng nói: "{request.message}"
            
            Thông tin người dùng:
            - Danh mục ưa thích: {user_profile.get('preferred_category', 'không rõ')}
            - Thương hiệu ưa thích: {user_profile.get('preferred_brand', 'không rõ')}
            - Khoảng giá: {user_profile.get('price_min', 0):,} - {user_profile.get('price_max', 1000000):,} VND
            
            Ngữ cảnh hiện tại:
            - Sản phẩm đang xem: {context.get('recent_views', [])}
            - Tìm kiếm gần đây: {context.get('recent_searches', [])}
            - Giỏ hàng: {context.get('cart_items', [])}
            
            Hãy phân tích và trả về JSON mô tả chiến lược gợi ý phù hợp.
            """
            
            # Get recommendation strategy from agent
            agent_response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract recommendation query from response
            recommendation_info = self._extract_recommendation_query(agent_response)
            
            # Execute recommendation strategy
            recommendations = self._execute_recommendation_strategy(
                recommendation_info, 
                user_profile, 
                context
            )
            
            # Generate human-friendly response
            response_text = self._generate_response(recommendations, recommendation_info)
            
            # Prepare context used for the recommendation
            context_used = {
                "user_profile": {
                    "preferred_category": user_profile.get("preferred_category"),
                    "preferred_brand": user_profile.get("preferred_brand"),
                    "price_range": {
                        "min": user_profile.get("price_min"),
                        "max": user_profile.get("price_max")
                    }
                },
                "context_features": {
                    k: v for k, v in context.items() if v  # Include only non-empty context features
                }
            }
            
            # Return response
            return RecommendationResponse(
                content=response_text,
                recommendations=recommendations,
                recommendation_type=recommendation_info.get("recommendation_type", "trending"),
                context_used=context_used
            )
            
        except Exception as e:
            logger.error(f"Error processing recommendation: {e}")
            # Return error response
            return RecommendationResponse(
                content=f"Đã xảy ra lỗi khi xử lý gợi ý: {str(e)}",
                recommendations=[],
                recommendation_type="trending",
                context_used={}
            )


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_products(request: RecommendationRequest):
    """Endpoint to get personalized product recommendations."""
    try:
        agent = RecommendationAgent()
        return await agent.process_recommendation(request)
    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing recommendation: {str(e)}") 