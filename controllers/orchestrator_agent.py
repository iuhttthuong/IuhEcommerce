import json
import re
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import random
import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
import time

from env import env
from models.chats import ChatMessageCreate
from repositories.message import MessageRepository

router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

class OrchestratorRequest(BaseModel):
    chat_id: int
    message: str

class OrchestratorResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    source_agent: str = Field(..., description="Agent xử lý yêu cầu")
    intent: str = Field(..., description="Ý định được phát hiện")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Các thực thể được trích xuất")
    confidence: float = Field(..., description="Độ tin cậy của phân loại")

class OrchestratorAgent:
    """
    The Orchestrator Agent analyzes user messages, determines intent, 
    extracts entities, and routes requests to the appropriate specialized agent.
    """
    
    def __init__(self):
        """Initialize the Orchestrator Agent with necessary configurations and models."""
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        # Initialize components in the correct order
        self.intent_classes = self._get_intent_classes()
        self.vectorizer = self._load_or_create_vectorizer()
        self.intent_model = self._load_or_train_intent_model()
        self.agent = self._create_orchestrator_agent()
        
        # Define agent routing map for intent to agent mapping
        self.agent_routing = {
            "product_search": "search_discovery_agent",
            "product_info": "product_info_agent",
            "recommendation": "recommendation_agent",
            "compare_products": "product_comparison_agent",
            "review_inquiry": "review_agent",
            "user_profile": "user_profile_agent",
            "policy_question": "policy_agent",
            "general_inquiry": "qdrant_agent",
            "support_request": "qdrant_agent",
            "cart_management": "qdrant_agent",
            "order_tracking": "qdrant_agent"
        }

    def _get_intent_classes(self) -> List[str]:
        """Return list of supported intent classes."""
        return [
            "product_search", "product_info", "recommendation", 
            "compare_products", "review_inquiry", "user_profile", 
            "policy_question", "cart_management", "order_tracking", 
            "general_inquiry", "support_request"
        ]

    def _load_or_create_vectorizer(self) -> TfidfVectorizer:
        """Load TF-IDF vectorizer from disk or create a new one with sample data."""
        vectorizer_path = "models/intent_vectorizer.pkl"
        
        if os.path.exists(vectorizer_path):
            try:
                with open(vectorizer_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading vectorizer: {e}")
                
        # Create new vectorizer with mock training data
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Sample user queries for training
        sample_queries = self._generate_sample_queries()
        
        # Fit vectorizer
        vectorizer.fit(sample_queries)
        
        # Save vectorizer
        os.makedirs("models", exist_ok=True)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
            
        return vectorizer

    def _generate_sample_queries(self) -> List[str]:
        """Generate sample queries for different intents to train the vectorizer."""
        queries = []
        
        # Product search queries
        queries.extend([
            "Tìm điện thoại Samsung mới nhất",
            "Tôi muốn tìm laptop dưới 20 triệu",
            "Có sản phẩm nào về camera không",
            "Tìm giày Nike size 42",
            "Tôi đang tìm kiếm sách về lập trình"
        ])
        
        # Product info queries
        queries.extend([
            "Cho tôi thông tin về iPhone 13",
            "Thông số kỹ thuật của laptop Dell XPS 15",
            "Sản phẩm này có những màu nào",
            "Dung lượng pin của sản phẩm này là bao nhiêu",
            "Samsung S23 Ultra có chống nước không"
        ])
        
        # Recommendation queries
        queries.extend([
            "Gợi ý cho tôi vài mẫu áo phông đẹp",
            "Có sản phẩm nào tương tự như iPhone nhưng rẻ hơn không",
            "Giới thiệu cho tôi vài cuốn sách hay",
            "Tôi nên mua camera nào để chụp phong cảnh",
            "Đề xuất laptop tốt cho đồ họa"
        ])
        
        # Compare products queries
        queries.extend([
            "So sánh iPhone 13 và Samsung S22",
            "iPhone và Samsung khác nhau thế nào",
            "So sánh hai laptop này",
            "MacBook Air và Dell XPS đâu tốt hơn",
            "Phân tích ưu nhược điểm của hai sản phẩm này"
        ])
        
        # Review inquiry queries
        queries.extend([
            "Đánh giá về sản phẩm này thế nào",
            "Người dùng nói gì về iPhone 13",
            "Xem review Samsung S22",
            "Có ai phàn nàn về sản phẩm này không",
            "Ưu điểm và nhược điểm của sản phẩm theo đánh giá người dùng"
        ])
        
        # User profile queries
        queries.extend([
            "Thông tin tài khoản của tôi",
            "Cập nhật địa chỉ giao hàng",
            "Đổi mật khẩu",
            "Xem lại sở thích của tôi",
            "Cập nhật thông tin cá nhân"
        ])
        
        # Add more categories as needed
        
        return queries

    def _load_or_train_intent_model(self):
        """Load XGBoost intent classification model from disk or train a new one."""
        model_path = "models/intent_model.xgb"
        
        # Check if model exists
        if os.path.exists(model_path):
            try:
                return xgb.Booster(model_file=model_path)
            except Exception as e:
                logger.error(f"Error loading XGBoost model: {e}")
        
        # If model doesn't exist or loading failed, train a new one
        logger.info("Training new XGBoost intent classification model")
        
        try:
            # Generate training data
            X_train, y_train = self._generate_intent_training_data()
            
            # Train XGBoost model
            dtrain = xgb.DMatrix(X_train, label=y_train)
            param = {
                'max_depth': 5, 
                'eta': 0.1, 
                'objective': 'multi:softprob',
                'num_class': len(self.intent_classes),
                'eval_metric': 'mlogloss'
            }
            
            num_rounds = 100
            model = xgb.train(param, dtrain, num_rounds)
            
            # Save model
            os.makedirs("models", exist_ok=True)
            model.save_model(model_path)
            
            return model
        except Exception as e:
            logger.error(f"Error training intent model: {e}")
            return None

    def _generate_intent_training_data(self):
        """Generate synthetic data for training the intent classification model."""
        # Sample queries for different intents
        intent_queries = {
            "product_search": [
                "Tìm điện thoại Samsung",
                "Tìm laptop dưới 20 triệu",
                "Tôi muốn tìm kiếm camera",
                "Tìm giày Nike size 42",
                "Có sản phẩm nào về smartwatch không",
                "Tìm áo phông nam",
                "Tôi cần tìm sách về lập trình",
                "Tìm kiếm tai nghe không dây",
                "Có phụ kiện nào cho iPhone không",
                "Tìm sản phẩm giảm giá"
            ],
            "product_info": [
                "Thông tin về iPhone 13",
                "Thông số kỹ thuật của laptop Dell XPS",
                "Samsung S22 có những màu nào",
                "Pin của iPad Pro dùng được bao lâu",
                "Cấu hình của máy tính này",
                "Chất liệu của sản phẩm này là gì",
                "iPhone 14 có chống nước không",
                "Kích thước của TV Sony 55 inch",
                "Bảo hành sản phẩm này thế nào",
                "Xuất xứ của sản phẩm này ở đâu"
            ],
            # Continue with other intents...
        }
        
        # Generate X_train and y_train
        X = []
        y = []
        
        for i, intent in enumerate(self.intent_classes):
            if intent in intent_queries:
                # Add original queries
                queries = intent_queries[intent]
                X.extend(queries)
                y.extend([i] * len(queries))
                
                # Add variations of each query
                for query in queries:
                    variations = self._generate_query_variations(query)
                    X.extend(variations)
                    y.extend([i] * len(variations))
        
        # Vectorize the text
        X_vec = self.vectorizer.transform(X).toarray()
        
        return X_vec, np.array(y)

    def _generate_query_variations(self, query: str, num_variations: int = 3) -> List[str]:
        """Generate variations of a query to expand training data."""
        variations = []
        
        # Simple word replacements (Vietnamese)
        replacements = {
            "tìm": ["kiếm", "tìm kiếm", "tìm hiểu về"],
            "thông tin": ["chi tiết", "mô tả", "thông số"],
            "gợi ý": ["đề xuất", "giới thiệu", "cho tôi biết"],
            "so sánh": ["đối chiếu", "phân biệt", "khác nhau"],
            "đánh giá": ["review", "nhận xét", "ý kiến"],
            "sản phẩm": ["hàng", "mặt hàng", "item"]
        }
        
        # Generate variations by replacing words and adding/removing fillers
        for _ in range(num_variations):
            variation = query
            
            # Replace a random word if possible
            for word, alternatives in replacements.items():
                if word in variation.lower() and random.random() < 0.3:
                    replacement = random.choice(alternatives)
                    variation = re.sub(r'\b' + word + r'\b', replacement, variation, flags=re.IGNORECASE, count=1)
            
            # Add or remove filler words
            fillers = ["cho tôi", "vui lòng", "tôi muốn", "có thể"]
            if random.random() < 0.3:
                # Add filler
                filler = random.choice(fillers)
                if filler not in variation.lower():
                    variation = filler + " " + variation
            elif random.random() < 0.3 and any(f in variation.lower() for f in fillers):
                # Remove filler
                for filler in fillers:
                    variation = re.sub(r'\b' + filler + r'\b\s*', '', variation, flags=re.IGNORECASE)
            
            if variation != query and variation not in variations:
                variations.append(variation)
        
        return variations

    def _predict_intent(self, message: str) -> Dict[str, Any]:
        """Predict the intent of a user message using the trained model."""
        try:
            if not self.intent_model or not self.vectorizer:
                # Fallback to default intent if models aren't available
                logger.warning("Intent models not available, using fallback")
                return {
                    "intent": "general_inquiry",
                    "confidence": 0.5
                }
            
            # Vectorize the message
            message_vec = self.vectorizer.transform([message]).toarray()
            
            # Predict probabilities
            dtest = xgb.DMatrix(message_vec)
            probabilities = self.intent_model.predict(dtest)[0]
            
            # Get the most likely intent
            max_prob_idx = np.argmax(probabilities)
            max_prob = probabilities[max_prob_idx]
            predicted_intent = self.intent_classes[max_prob_idx]
            
            return {
                "intent": predicted_intent,
                "confidence": float(max_prob),
                "all_probabilities": {intent: float(prob) for intent, prob in zip(self.intent_classes, probabilities)}
            }
        except Exception as e:
            logger.error(f"Error predicting intent: {e}")
            return {
                "intent": "general_inquiry",
                "confidence": 0.5
            }

    def _create_orchestrator_agent(self) -> ConversableAgent:
        """Create and configure the orchestrator agent with system message."""
        system_message = """
        Bạn là Orchestrator Agent thông minh cho hệ thống thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. Phân tích tin nhắn người dùng để xác định ý định (intent)
        2. Trích xuất các thực thể quan trọng (entities) từ tin nhắn
        3. Quyết định agent nào phù hợp nhất để xử lý yêu cầu
        
        Các loại intent có thể có:
        - product_search: Tìm kiếm sản phẩm
        - product_info: Thông tin chi tiết về sản phẩm
        - recommendation: Gợi ý sản phẩm
        - compare_products: So sánh sản phẩm
        - review_inquiry: Hỏi về đánh giá/review
        - user_profile: Liên quan đến thông tin người dùng
        - policy_question: Câu hỏi về chính sách
        - cart_management: Quản lý giỏ hàng
        - order_tracking: Theo dõi đơn hàng
        - general_inquiry: Câu hỏi chung
        - support_request: Yêu cầu hỗ trợ
        
        Trả về duy nhất một JSON với cấu trúc:
        
        ```json
        {
            "intent": "loại_intent_đã_phát_hiện",
            "entities": {
                "product_name": "tên sản phẩm (nếu có)",
                "product_id": "id sản phẩm (nếu có)",
                "category": "danh mục (nếu có)",
                "price_range": {"min": 0, "max": 1000000},
                "attributes": ["thuộc tính 1", "thuộc tính 2"]
            },
            "target_agent": "tên_agent_để_xử_lý_yêu_cầu",
            "confidence": 0.95 // độ tin cậy của phân loại
        }
        ```
        """
        return autogen.ConversableAgent(
            name="orchestrator",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_orchestrator_result(self, response: str) -> Dict[str, Any]:
        """Extract JSON result from agent response with robust error handling."""
        try:
            # Find JSON in the response
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                
                # Validate required fields
                if not result.get("intent") or not result.get("target_agent"):
                    logger.warning("Missing required fields in orchestrator result")
                    result["intent"] = result.get("intent", "general_inquiry")
                    result["target_agent"] = result.get("target_agent", "qdrant_agent")
                
                # Ensure other fields exist
                result["entities"] = result.get("entities", {})
                result["confidence"] = result.get("confidence", 0.7)
                
                return result
            else:
                logger.warning(f"No JSON found in orchestrator response: {response}")
                return {
                    "intent": "general_inquiry",
                    "entities": {},
                    "target_agent": "qdrant_agent",
                    "confidence": 0.5
                }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}")
            return {
                "intent": "general_inquiry",
                "entities": {},
                "target_agent": "qdrant_agent",
                "confidence": 0.5
            }

    async def route_to_agent(self, target_agent: str, request: OrchestratorRequest, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to the appropriate agent for processing.
        
        Args:
            target_agent: The name of the agent to handle the request
            request: The original user request
            entities: Extracted entities from the user message
            
        Returns:
            The response from the target agent
        """
        # Dynamic imports to avoid circular imports
        try:
            logger.info(f"Routing request to {target_agent}")
            
            if target_agent == "search_discovery_agent":
                from controllers.search_discovery_agent import SearchDiscoveryAgent
                agent = SearchDiscoveryAgent()
                return await agent.process_search(query=request.message, entities=entities)
                
            elif target_agent == "product_info_agent":
                from controllers.product_info_agent import ProductInfoAgent, ProductInfoRequest
                agent = ProductInfoAgent()
                product_id = entities.get("product_id")
                return await agent.process_request(ProductInfoRequest(
                    chat_id=request.chat_id, 
                    message=request.message, 
                    product_id=product_id, 
                    entities=entities
                ))
                
            elif target_agent == "recommendation_agent":
                from controllers.recommendation_agent import RecommendationAgent, RecommendationRequest
                agent = RecommendationAgent()
                user_id = entities.get("user_id")
                context = {
                    "entities": entities,
                    "recent_views": entities.get("recent_views", []),
                    "recent_searches": entities.get("recent_searches", [])
                }
                return await agent.process_recommendation(RecommendationRequest(
                    chat_id=request.chat_id, 
                    user_id=user_id,
                    message=request.message, 
                    context=context
                ))
                
            elif target_agent == "product_comparison_agent":
                from controllers.product_comparison_agent import ProductComparisonAgent
                agent = ProductComparisonAgent()
                return await agent.process_comparison(request.message, entities)
                
            elif target_agent == "review_agent":
                from controllers.review_agent import ReviewAgent
                agent = ReviewAgent()
                return await agent.process_review(request.message, entities)
                
            elif target_agent == "user_profile_agent":
                from controllers.user_profile_agent import UserProfileAgent
                agent = UserProfileAgent()
                return await agent.process_profile(request.chat_id, request.message, entities)
                
            elif target_agent == "policy_agent":
                from controllers.polici_agent import PolicyAgent
                agent = PolicyAgent()
                return await agent.process_policy(request.message, entities)
                
            else:
                # Default to Qdrant agent for general inquiries
                logger.info(f"Unknown agent '{target_agent}', defaulting to qdrant_agent")
                from controllers.qdrant_agent import QdrantAgent
                agent = QdrantAgent()
                response = await agent.process_query(request.message, request.chat_id)
                return response
                
        except ImportError as e:
            logger.error(f"Import error when routing to {target_agent}: {str(e)}")
            logger.info(f"Falling back to qdrant_agent due to import error")
            try:
                from controllers.qdrant_agent import QdrantAgent
                agent = QdrantAgent()
                response = await agent.process_query(request.message, request.chat_id)
                return response
            except Exception as fallback_error:
                logger.error(f"Fallback to Qdrant agent failed: {str(fallback_error)}")
                return {"content": "Đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."}
        
        except Exception as e:
            logger.error(f"Error routing to agent {target_agent}: {str(e)}")
            # Fallback to Qdrant agent in case of error
            try:
                from controllers.qdrant_agent import QdrantAgent
                agent = QdrantAgent()
                response = await agent.process_query(request.message, request.chat_id)
                return response
            except Exception as fallback_error:
                logger.error(f"Fallback to Qdrant agent failed: {str(fallback_error)}")
                return {"content": "Đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."}

    async def process_request(self, request: OrchestratorRequest) -> Dict[str, Any]:
        """
        Process a user request through the orchestrator pipeline.
        
        The method performs the following steps:
        1. Predicts the user intent using the ML model
        2. Confirms and refines the intent using LLM
        3. Extracts entities from the user message
        4. Routes the request to the appropriate specialized agent
        5. Returns the formatted response
        
        Args:
            request: The user request containing a message and chat ID
            
        Returns:
            A dictionary with the agent response and metadata
        """
        try:
            # Step 1: Use ML model to predict intent
            ml_intent_prediction = self._predict_intent(request.message)
            predicted_intent = ml_intent_prediction["intent"]
            confidence = ml_intent_prediction["confidence"]
            
            logger.info(f"ML intent prediction: {predicted_intent} (confidence: {confidence:.2f})")
            
            # Step 2: Use LLM for advanced intent recognition and entity extraction
            prompt = f"""
            Phân tích tin nhắn từ người dùng trong một hệ thống thương mại điện tử:
            
            "{request.message}"
            
            Mô hình ML đã dự đoán ý định là: {predicted_intent} (độ tin cậy: {confidence:.2f})
            
            Hãy phân tích kỹ tin nhắn này để:
            1. Xác nhận hoặc điều chỉnh phân loại ý định
            2. Trích xuất tất cả các thực thể liên quan (sản phẩm, thuộc tính, khoảng giá, v.v.)
            3. Xác định agent thích hợp nhất để xử lý yêu cầu này
            
            Trả về JSON với phân tích của bạn theo đúng định dạng đã hướng dẫn.
            """
            
            # Generate agent response
            agent_response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract structured result
            orchestrator_result = self._extract_orchestrator_result(agent_response)
            
            # Combine ML confidence with LLM decision
            final_intent = orchestrator_result["intent"]
            final_confidence = max(confidence, orchestrator_result.get("confidence", 0))
            
            # Map intent to target agent if not specified
            target_agent = orchestrator_result.get("target_agent")
            if not target_agent and final_intent in self.agent_routing:
                target_agent = self.agent_routing[final_intent]
            elif not target_agent:
                target_agent = "qdrant_agent"  # Default agent
            
            logger.info(f"Routing to agent: {target_agent} for intent: {final_intent}")
            
            # Extract entities with fallback for empty values
            entities = orchestrator_result.get("entities", {})
            
            # Normalize entity values (convert string numbers to integers where appropriate)
            normalized_entities = {}
            for key, value in entities.items():
                if isinstance(value, str) and value.isdigit() and key in ["product_id", "user_id", "category_id"]:
                    normalized_entities[key] = int(value)
                else:
                    normalized_entities[key] = value
                    
            # Route to appropriate agent
            response = await self.route_to_agent(target_agent, request, normalized_entities)
            
            # Format final response
            if isinstance(response, dict):
                if "content" in response:
                    content = response["content"]
                else:
                    content = str(response)
            else:
                content = str(response)
                
            # Prepare result including metadata
            result = {
                "content": content,
                "source_agent": target_agent,
                "intent": final_intent,
                "entities": normalized_entities,
                "confidence": final_confidence
            }
            
            # Save interaction data to message repository if needed
            try:
                message_repository = MessageRepository()
                message_payload = ChatMessageCreate(
                    chat_id=request.chat_id,
                    sender_type="assistant",
                    sender_id=0,  # You may need to adjust this based on your requirements
                    content=content,
                    metadata={
                        "intent": final_intent,
                        "source_agent": target_agent,
                        "entities": normalized_entities,
                        "confidence": final_confidence
                    }
                )
                message_repository.create(message_payload)
            except Exception as repo_error:
                logger.error(f"Error saving to message repository: {str(repo_error)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in orchestrator process_request: {str(e)}")
            # Return error response
            error_response = {
                "content": f"Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại.",
                "source_agent": "orchestrator",
                "intent": "error",
                "entities": {},
                "confidence": 0.0
            }
            
            # Try to log error message
            try:
                message_repository = MessageRepository()
                message_payload = ChatMessageCreate(
                    chat_id=request.chat_id,
                    sender_type="assistant",
                    sender_id=0,  # You may need to adjust this based on your requirements
                    content=error_response["content"],
                    metadata={"error": str(e)}
                )
                message_repository.create(message_payload)
            except:
                pass
                
            return error_response


@router.post("/process", response_model=OrchestratorResponse, 
         description="Process a user message through the orchestrator pipeline")
async def process_request(request: OrchestratorRequest):
    """
    Process a user message through the orchestrator pipeline.
    
    This endpoint:
    1. Analyzes the message to determine intent
    2. Extracts relevant entities
    3. Routes the request to the appropriate agent
    4. Returns the formatted response
    
    Args:
        request: The user request containing a message and chat ID
        
    Returns:
        OrchestratorResponse: The formatted response with metadata
        
    Raises:
        HTTPException: If an error occurs during processing
    """
    start_time = time.time()
    
    try:
        # Create orchestrator agent
        agent = OrchestratorAgent()
        
        # Process the request
        response = await agent.process_request(request)
        
        # Log processing time
        processing_time = time.time() - start_time
        logger.info(f"Request processed in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        # Log detailed error
        logger.error(f"Error in orchestrator endpoint: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500, 
            detail="Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."
        ) 