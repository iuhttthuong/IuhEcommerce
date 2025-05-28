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
from models.chatbot_models import ChatbotRequest, AgentMessage, AgentResponse
from autogen import register_function
from env import env
from typing import Optional, Dict, Any, List
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
from controllers.synthetic import chatbot_reply, chatbot_output


api_url =  "http://localhost:8000"

router = APIRouter(prefix="/manager", tags=["Manager"])
# Lấy cấu hình model từ môi trường
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]

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
async def call_agent(agent, request: ChatbotRequest, raw_message: Optional[str] = None):
    try:
        agent_id = str(uuid.uuid4())
        agent_type = agent

        # Create agent message
        agent_message = AgentMessage(
            agent_id=agent_id,
            agent_type=agent_type,
            content=request.message,
            metadata={"context": request.context, "entities": request.entities}
        )

        # Process with specific agent
        if agent == "ProductAgent":
            result = await product_agent(request)
            # Convert AgentResponse to dict format
            if isinstance(result, AgentResponse):
                result = {
                    "message": result.content,
                    "type": "product",
                    "data": result.metadata
                }
        elif agent == "PoliciAgent":
            from controllers.polici_agent import ask_chatbot as policy_ask_chatbot
            logger.info(f"Calling policy_ask_chatbot with request: {request}")
            result = policy_ask_chatbot(request)
            logger.info(f"Policy agent result: {result}")

            # Nếu result là dict kiểu {'response': ...}, lấy giá trị response
            if isinstance(result, dict) and "response" in result:
                answer = result["response"]
                logger.info(f"Extracted answer from response: {answer}")
            else:
                answer = str(result)
                logger.info(f"Using string result as answer: {answer}")

            result = {
                "message": answer,
                "type": "policy",
                "data": {"answer": answer}
            }
            logger.info(f"Final formatted result: {result}")
        elif agent == "MySelf":
            result = {
                "message": "Xin chào! Tôi là trợ lý AI của IUH-Ecomerce. Tôi có thể giúp gì cho bạn?",
                "type": "greeting"
            }
        elif agent == "TransactionAgent":
            search_results = await search(request.message, collection_name="product_embeddings", limit=5)
            # Convert search results to dict format
            result = {
                "message": "Kết quả tìm kiếm giao dịch",
                "type": "transaction",
                "data": search_results
            }
        elif agent == "OrchestratorAgent":
            orchestrator = OrchestratorAgent()
            result = await orchestrator.process_request(request)
        elif agent == "UserProfileAgent":
            from db import SessionLocal
            db = SessionLocal()
            try:
                user_profile = UserProfileAgent(db)
                user_request = UserProfileRequest(
                    chat_id=request.chat_id,
                    user_id=request.user_id,
                    message=request.message,
                    entities=request.entities or {}
                )
                result = await user_profile.process_request(user_request)
                result = {
                    "message": result.content,
                    "type": "user_profile",
                    "user_data": result.user_data,
                    "success": result.success
                }
            finally:
                db.close()
        elif agent == "SearchDiscoveryAgent":
            search_agent = SearchDiscoveryAgent()
            result = await search_agent.process_search(request)
            # Convert SearchResponse to dict format
            if hasattr(result, 'content'):
                result = {
                    "message": result.content,
                    "type": "search",
                    "data": result.dict() if hasattr(result, 'dict') else result
                }
        elif agent == "RecommendationAgent":
            recommendation_agent = RecommendationAgent()
            result = await recommendation_agent.process_recommendation(request)
        elif agent == "ProductInfoAgent":
            product_info_agent = ProductInfoAgent()
            result = await product_info_agent.process_request(request)
        elif agent == "ReviewAgent":
            db = Session()
            try:
                review_agent = ReviewAgent(db)
                result = await review_agent.process_request(request)
                # Convert ReviewResponse to dict format
                result = {
                    "message": result.content,
                    "type": "review",
                    "data": {
                        "product_id": result.product_id,
                        "review_summary": result.review_summary
                    }
                }
            finally:
                db.close()
        elif agent == "ProductComparisonAgent":
            comparison_agent = ProductComparisonAgent()
            result = await comparison_agent.process_request(request)
        else:
            result = {
                "message": "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                "type": "error"
            }

        # Create agent response
        if isinstance(result, dict):
            content = result.get("message", str(result))
            metadata = {"type": result.get("type"), "data": result}
        else:
            content = str(result)
            metadata = {"type": "unknown", "data": str(result)}

        agent_response = AgentResponse(
            agent_id=agent_id,
            agent_type=agent_type,
            content=content,
            metadata=metadata
        )

        # Save agent message and response
        message_payload = ChatMessageCreate(
            chat_id=request.chat_id,
            content=request.message,
            sender_type="agent",
            sender_id=agent_id,
            message_metadata={"agent_type": agent_type}
        )
        # MessageRepository.create_message(message_payload)

        # Convert AgentResponse to dict for database storage
        response_metadata = {
            "agent_type": agent_type,
            "response_data": {
                "content": agent_response.content,
                "type": metadata.get("type"),
                "data": metadata.get("data")
            }
        }

        final_agent_response = await chatbot_output(agent_response.content, raw_message)
        print(f"🤣💕🤣➡️🤷‍♂️❎{final_agent_response}")
        response_payload = ChatMessageCreate(
            chat_id=request.chat_id,
            content=final_agent_response,
            sender_type="agent_response",
            sender_id=agent_id,
            message_metadata=response_metadata
        )
        MessageRepository.create_message(response_payload)
        print("Đã lưu phản hồi của agent vào cơ sở dữ liệu.")
        return final_agent_response
    except Exception as e:
        logger.error(f"Error in call_agent: {str(e)}")
        return AgentResponse(
            agent_id=agent_id,
            agent_type=agent_type,
            content="Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
            metadata={"type": "error", "error": str(e)}
        )

@router.post("/ask")
async def ask_chatbot(request: ChatbotRequest):
    try:
        raw_message = request.message
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
                sender_id=str(request.user_id or 1),  # Convert to string
                message_metadata={"user_id": request.user_id}
            )
            MessageRepository.create_message(message_payload)

            # Gửi tin nhắn đến chatbot để lấy prompt
            message = await chatbot_reply(message, chat_id = request.chat_id , api_url = api_url)

            # Process message and get agent response
            response = await get_product_info(message)
            agent = response.get("agent")
            query = response.get("query")
            request.message = query  # Update request message with the query
            if agent and query:
                result = await call_agent(agent, request, raw_message)
                return await chatbot_output(result, raw_message)

            else:
                return {
                    "message": "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này.",
                    "type": "error"
                }

        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in ask_chatbot: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/chat", response_model=AgentResponse)
async def chat_with_manager(payload: ChatbotRequest):
    try:
        raw_message = payload.message
        # Process message and get agent response
        response = await get_product_info(payload.message)
        agent = response.get("agent")
        query = response.get("query")

        if agent and query:
            result = await call_agent(agent, payload, raw_message)
            return await chatbot_output(result, raw_message)

        return AgentResponse(
            agent_id="manager",
            agent_type="manager",
            content="Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này.",
            metadata={"type": "error"}
        )

    except Exception as e:
        logger.error(f"Error in chat_with_manager: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
