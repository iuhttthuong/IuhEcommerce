from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os, json, dotenv
from autogen import AssistantAgent, ConversableAgent
import uuid
from db import Session
from models.fqas import FQA
from repositories.message import MessageRepository
from controllers.search import search
import traceback
from models.chats import ChatMessage, ChatMessageCreate, ChatCreate
from autogen import register_function
from env import env
from typing import Optional, Dict, Any
from loguru import logger

from controllers.qdrant_agent import chatbot_endpoint as product_agent
from controllers.polici_agent import ask_chatbot as policy_agent
from controllers.orchestrator_agent import OrchestratorAgent
from controllers.user_profile_agent import UserProfileAgent, UserProfileRequest
from controllers.search_discovery_agent import SearchDiscoveryAgent
from controllers.recommendation_agent import RecommendationAgent
from controllers.product_info_agent import ProductInfoAgent
from controllers.review_agent import ReviewAgent
from controllers.product_comparison_agent import ProductComparisonAgent
from services.manager import ManagerService

router = APIRouter(prefix="/manager", tags=["Manager"])
# Lấy cấu hình model từ môi trường
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]
class ChatbotRequest(BaseModel):
    chat_id: int
    message: str
    context: dict = None
    user_id: Optional[int] = None
    shop_id: Optional[int] = None  # Add shop_id field
    entities: Optional[Dict[str, Any]] = None


Manager = ConversableAgent(
    name="manager",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecomerce
    Bạn sẽ nhận đầu vào câu hỏi của người dùng về sàn thương mại điện tử IUH-Ecomerce
    Nhiệm vụ của bạn là trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể
    Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin
    Hãy trả về mô tả truy vấn Qdrant dưới dạng JSON:"
        "agent": "ProductAgent" | "PoliciAgent" | "MySelf" | "TransactionAgent" | "OrchestratorAgent" | "UserProfileAgent" | "SearchDiscoveryAgent" | "RecommendationAgent" | "ProductInfoAgent" | "ReviewAgent" | "ProductComparisonAgent",
        "query": String
    Với Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin
        Trong đó ProductAgent là trợ lý tìm kiếm thông tin sản phẩm
        Trong đó PoliciAgent là trợ lý tìm kiếm thông tin chính sách
        Trong đó MySelf là trợ lý tìm trả lời câu hỏi bình thường
        Trong đó TransactionAgent là trợ lý tìm kiếm thông tin giao dịch
        Trong đó OrchestratorAgent là trợ lý điều phối NLU xử lý ý định và thực thể
        Trong đó UserProfileAgent là trợ lý quản lý thông tin người dùng
        Trong đó SearchDiscoveryAgent là trợ lý tìm kiếm và khám phá sản phẩm
        Trong đó RecommendationAgent là trợ lý gợi ý sản phẩm cá nhân hóa
        Trong đó ProductInfoAgent là trợ lý cung cấp thông tin chi tiết về sản phẩm
        Trong đó ReviewAgent là trợ lý phân tích đánh giá sản phẩm
        Trong đó ProductComparisonAgent là trợ lý so sánh sản phẩm

        """,    

        
    llm_config={"config_list": config_list},
    human_input_mode= "NEVER"
)

async def get_product_info(query):
    chat = await Manager.a_generate_reply(
    messages=[{"role": "user", "content": query}])
    print(f"Chat: {chat}")
    
    # Extract JSON from the response content
    content = chat.get('content', '')
    try:
        # Find JSON in the content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            response = json.loads(json_str)
        else:
            # If no JSON found, create a default response
            response = {
                "agent": "MySelf",
                "query": query
            }
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        # Fallback to default response
        response = {
            "agent": "MySelf",
            "query": query
        }
    return response



### call agent
async def call_agent(agent, request): 
    try:
        if agent == "ProductAgent":
            # Gọi hàm tìm kiếm sản phẩm
            result = await product_agent(request)
            return result
        elif agent == "PoliciAgent":
            # Gọi hàm tìm kiếm chính sách
            result = policy_agent(request)
            return result
        elif agent == "MySelf":
            # For MySelf agent, return a friendly response directly
            return {
                "message": "Xin chào! Tôi là trợ lý AI của IUH-Ecomerce. Tôi có thể giúp gì cho bạn?",
                "type": "greeting"
            }
        elif agent == "TransactionAgent":
            # Gọi hàm tìm kiếm thông tin giao dịch
            result = await search(request.message)
            return result
        elif agent == "OrchestratorAgent":
            # Gọi orchestrator agent
            orchestrator = OrchestratorAgent()
            result = await orchestrator.process_request(request)
            return result
        elif agent == "UserProfileAgent":
            # Gọi user profile agent
            user_profile = UserProfileAgent()
            # Convert ChatbotRequest to UserProfileRequest
            user_request = UserProfileRequest(
                chat_id=request.chat_id,
                user_id=request.user_id,
                message=request.message,
                entities=request.entities or {}
            )
            result = await user_profile.process_request(user_request)
            # Convert UserProfileResponse to dict format
            return {
                "message": result.content,
                "type": "user_profile",
                "user_data": result.user_data,
                "success": result.success
            }
        elif agent == "SearchDiscoveryAgent":
            # Gọi search discovery agent
            search_agent = SearchDiscoveryAgent()
            result = await search_agent.process_search(request)
            return result
        elif agent == "RecommendationAgent":
            # Gọi recommendation agent
            recommendation_agent = RecommendationAgent()
            result = await recommendation_agent.process_recommendation(request)
            return result
        elif agent == "ProductInfoAgent":
            # Gọi product info agent
            product_info_agent = ProductInfoAgent()
            result = await product_info_agent.process_request(request)
            return result
        elif agent == "ReviewAgent":
            # Gọi review agent
            review_agent = ReviewAgent()
            result = await review_agent.process_request(request)
            return result
        elif agent == "ProductComparisonAgent":
            # Gọi product comparison agent
            comparison_agent = ProductComparisonAgent()
            result = await comparison_agent.process_request(request)
            return result
        else:
            return {
                "message": "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                "type": "error"
            }
    except Exception as e:
        logger.error(f"Error in call_agent: {str(e)}")
        return {
            "message": "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            "type": "error",
            "error": str(e)
        }

@router.post("/ask")
async def ask_chatbot(request: ChatbotRequest):
    try:
        message = request.message
        print(f"Message: {message}")

        # Kiểm tra xem chat_id có tồn tại chưa
        from services.chat import ChatService
        from repositories.chat import ChatRepository
        from db import Session

        db = Session()
        try:
            chat_service = ChatService(db)
            
            if request.chat_id == 0 or request.chat_id is None:
                # Tạo chat mới với các giá trị mặc định
                new_chat = ChatCreate(
                    shop_id=request.shop_id or 1,  # Use provided shop_id or default to 1
                    customer_id=request.user_id  # Use provided user_id
                )
                chat = chat_service.create_session(new_chat)
                request.chat_id = chat.chat_id
                logger.info(f"Đã tạo chat mới với ID: {chat.chat_id}")
            else:
                # Kiểm tra xem chat_id đã tồn tại chưa
                try:
                    chat = chat_service.get_session(request.chat_id)
                    chat_exists = True
                except Exception as e:
                    # Tạo chat mới nếu không tìm thấy
                    new_chat = ChatCreate(
                        shop_id=request.shop_id or 1,  # Use provided shop_id or default to 1
                        customer_id=request.user_id  # Use provided user_id
                    )
                    chat = chat_service.create_session(new_chat)
                    request.chat_id = chat.chat_id
                    logger.info(f"Chat ID {request.chat_id} không tồn tại, đã tạo chat mới: {chat.chat_id}")

            # Lưu tin nhắn vào database
            message_payload = ChatMessageCreate(
                chat_id=request.chat_id,
                content=message,
                sender_type="customer",
                sender_id=request.user_id or 1  # Use provided user_id or default to 1
            )
            MessageRepository.create_message(message_payload)

            # Xử lý tin nhắn và gọi agent phù hợp
            response = await get_product_info(message)
            agent = response.get("agent")
            query = response.get("query")

            if agent and query:
                result = await call_agent(agent, request)
                
                # Lưu phản hồi của agent vào database
                try:
                    response_payload = ChatMessageCreate(
                        chat_id=request.chat_id,
                        content=result.get("message", str(result)),
                        sender_type="shop",
                        sender_id=request.shop_id if request.shop_id is not None else 1  # Use shop_id if available, otherwise default to 1
                    )
                    MessageRepository.create_message(response_payload)
                except Exception as e:
                    logger.error(f"Lỗi khi lưu phản hồi: {str(e)}")
                
                return result
            else:
                raise HTTPException(status_code=400, detail="Invalid response from manager")

        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Lỗi không xác định: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=dict)
def chat_with_manager(payload: ChatMessageCreate):
    try:
        response = ManagerService.process_message(payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

