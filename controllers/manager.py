from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json, dotenv
from autogen import AssistantAgent, ConversableAgent
import uuid
from db import Session
from models.fqas import FQA
from repositories.message import MessageRepository
from controllers.search import search
import traceback
from models.message import MessageModel, CreateMessagePayload
from autogen import register_function
from env import env

from controllers.qdrant_agent import chatbot_endpoint as product_agent
from controllers.polici_agent import ask_chatbot as policy_agent
from controllers.orchestrator_agent import OrchestratorAgent
from controllers.user_profile_agent import UserProfileAgent
from controllers.search_discovery_agent import SearchDiscoveryAgent
from controllers.recommendation_agent import RecommendationAgent
from controllers.product_info_agent import ProductInfoAgent
from controllers.review_agent import ReviewAgent
from controllers.product_comparison_agent import ProductComparisonAgent

router = APIRouter(prefix="/manager", tags=["Chatbot"])
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
    user_id: int = None
    context: dict = None


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
    response= json.loads(chat)
    return response



### call agent
async def call_agent(agent, request): 
    if agent == "ProductAgent":
        # Gọi hàm tìm kiếm sản phẩm
        result = await product_agent(request)
        return result
    elif agent == "PoliciAgent":
        # Gọi hàm tìm kiếm chính sách
        result = policy_agent(request)
        return result
    elif agent == "MySelf":
        # Gọi hàm tìm kiếm thông tin cá nhân
        result = await search(request.message)
        return result
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
        result = await user_profile.process_request(request)
        return result
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

@router.post("/ask")
async def ask_chatbot(request: ChatbotRequest):
    try:
        message = request.message
        print(f"Message: {message}")

        # Kiểm tra xem chat_id có tồn tại chưa hoặc nếu là 0 thì tạo mới
        from services.chat import ChatService
        from models.chat import ChatCreate
        from repositories.chat import ChatRepository
        from loguru import logger
        from repositories.customers import CustomerRepository
        from models.customers import CustomerCreate

        # Đảm bảo customer mặc định tồn tại trước khi thực hiện bất kỳ thao tác nào
        default_customer = CustomerRepository.get_or_create_default_customer()
        if not default_customer:
            error_message = "Không thể tạo customer mặc định, không thể tiếp tục."
            logger.error(error_message)
            return {"detail": error_message}
            
        # Sử dụng ID của customer mặc định đã tạo 
        default_user_id = default_customer.customer_id
        logger.info(f"Customer mặc định có ID: {default_user_id}")

        # Kiểm tra và đảm bảo user_id hợp lệ 
        user_id = request.user_id if request.user_id is not None else default_user_id
        
        # Đảm bảo user tồn tại - nếu không, sử dụng user mặc định
        try:
            if user_id != 0 and user_id != default_user_id:
                user = CustomerRepository.get_by_id(user_id)
                if not user:
                    # Nếu user không tồn tại nhưng ID được chỉ định, sử dụng user mặc định
                    user_id = default_user_id
                    logger.warning(f"User ID {request.user_id} không tồn tại, sử dụng user_id = {user_id}")
            else:
                # Nếu user_id = 0 hoặc trùng với mặc định, sử dụng user mặc định
                user_id = default_user_id
                logger.info(f"Sử dụng user mặc định với ID: {user_id}")
        except Exception as e:
            # Nếu có lỗi khi kiểm tra user, sử dụng user mặc định
            user_id = default_user_id
            logger.error(f"Lỗi khi kiểm tra user: {str(e)}. Sử dụng user_id = {user_id}")

        chat_exists = False
        try:
            if request.chat_id == 0 or request.chat_id is None:
                # Tạo chat mới với user_id đã kiểm tra
                new_chat = ChatCreate(user_id=user_id)
                chat = ChatService.create_chat(new_chat)
                request.chat_id = chat.id
                logger.info(f"Đã tạo chat mới với ID: {chat.id} cho user_id: {user_id}")
            else:
                # Kiểm tra xem chat_id đã tồn tại chưa
                try:
                    chat = ChatService.get_chat(request.chat_id)
                    chat_exists = True
                except Exception as e:
                    # Tạo chat mới nếu không tìm thấy
                    new_chat = ChatCreate(user_id=user_id)
                    chat = ChatService.create_chat(new_chat)
                    request.chat_id = chat.id
                    logger.info(f"Chat ID {request.chat_id} không tồn tại, đã tạo chat mới: {chat.id}")
        except Exception as e:
            # Log chi tiết lỗi khi tạo chat
            logger.error(f"Lỗi khi tạo hoặc kiểm tra chat: {str(e)}")
            # Nếu lỗi liên quan đến foreign key, thử tạo user trước
            if "foreign key" in str(e).lower():
                logger.info("Thử tạo người dùng mới trước khi tạo chat")
                # Logic tạo user nếu cần
            raise HTTPException(status_code=500, detail=f"Lỗi khi tạo chat: {str(e)}")

        # Lưu tin nhắn vào cơ sở dữ liệu với chat_id hợp lệ
        try:
            message_repository = MessageRepository()
            message_payload = CreateMessagePayload(
                chat_id=request.chat_id,
                role="user",
                content=message
            )
            message_repository.create(message_payload)
        except Exception as e:
            logger.error(f"Lỗi khi lưu tin nhắn: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu tin nhắn: {str(e)}")

        # Sử dụng Orchestrator Agent trước để phân tích ý định và thực thể
        orchestrator_request = {
            "chat_id": request.chat_id,
            "message": message
        }
        
        try:
            orchestrator = OrchestratorAgent()
            orchestrator_result = await orchestrator.process_request(orchestrator_request)
            
            # Lấy intent và entities từ kết quả orchestrator
            intent = orchestrator_result.get("intent", "unknown")
            entities = orchestrator_result.get("entities", {})
        except Exception as e:
            logger.error(f"Lỗi khi xử lý orchestrator: {str(e)}")
            intent = "unknown" 
            entities = {}
        
        # Tạo câu hỏi cho manager agent với thông tin về intent và entities
        question = f"""
        Người dùng hỏi: {message}
        
        Intent đã được phát hiện: {intent}
        Entities đã được trích xuất: {json.dumps(entities)}
        
        Vui lòng xác định agent phù hợp để xử lý yêu cầu này.
        """
        print(f"Question: {question}")
        
        try:
            # Gọi manager để xác định agent
            manager_response = await get_product_info(question)
            print(f"Manager Response: {manager_response}")
        except Exception as e:
            logger.error(f"Lỗi khi gọi manager: {str(e)}")
            # Fallback đến ProductAgent nếu có lỗi
            manager_response = {"agent": "ProductAgent", "query": message}
        
        # Bổ sung thông tin intent và entities vào request
        enhanced_request = ChatbotRequest(
            chat_id=request.chat_id,
            message=message,
            user_id=user_id,
            context={
                "intent": intent,
                "entities": entities
            }
        )
        
        try:
            # Gọi agent tương ứng
            result = await call_agent(manager_response["agent"], enhanced_request)
            print(f"Result: {result}")
        except Exception as e:
            logger.error(f"Lỗi khi gọi agent {manager_response['agent']}: {str(e)}")
            result = f"Rất tiếc, tôi đang gặp sự cố khi xử lý yêu cầu của bạn. Chi tiết lỗi: {str(e)}"
        
        # Lưu phản hồi từ agent vào cơ sở dữ liệu
        try:
            if isinstance(result, str):
                response_content = result
            else:
                # Nếu response có dạng khác, chuyển về string
                response_content = str(result)
                
            response_payload = CreateMessagePayload(
                chat_id=request.chat_id,
                role="assistant",
                content=response_content
            )
            message_repository.create(response_payload)
        except Exception as e:
            logger.error(f"Lỗi khi lưu kết quả vào database: {str(e)}")
        
        # Trả về kết quả
        return result

    except Exception as e:
        error_detail = f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}"
        logger.error(error_detail)
        traceback.print_exc()
        return {"detail": error_detail}

