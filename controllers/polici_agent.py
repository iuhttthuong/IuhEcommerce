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
from models.chats import ChatMessageCreate
from autogen import register_function
from env import env
from services.policy import PolicyService
from embedding.main import COLLECTIONS
import logging
from services.search import SearchServices
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Lấy cấu hình model từ môi trường
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": env.OPENAI_API_KEY,
        "api_type": "openai"
    }
]

class AgentMessage(BaseModel):
    agent_id: str
    agent_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatbotRequest(BaseModel):
    chat_id: int
    message: str
    context: Optional[dict] = None
    user_id: Optional[int] = None
    shop_id: Optional[int] = None
    entities: Optional[Dict[str, Any]] = None
    agent_messages: Optional[List[AgentMessage]] = None
    filters: Optional[Dict[str, Any]] = None

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

def search_faq(query: str, limit: int = 1):
    results = SearchServices.search(query, collection_name="faq_embeddings", limit=limit)
    if results and isinstance(results[0], dict):
        payload = results[0].get("payload")
        if payload and "answer" in payload:
            return payload["answer"]
    return "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn."

def get_fqa(payload: str, collection_name: str = "faq_embeddings", limit: int = 1):
    return search_faq(payload, limit)

# Cấu hình Assistant Agent
assistant = AssistantAgent(
    name="Assistant",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecomerce.
    Bạn sẽ nhận đầu vào câu hỏi của người dùng về các chính sách của sàn thương mại điện tử IUH-Ecomerce.
    Nhiệm vụ của bạn là tìm kiếm thông tin trong cơ sở dữ liệu và trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể.
    Hãy trả lời một cách thân thiện, tự nhiên và chuyên nghiệp. Sử dụng ngôn ngữ dễ hiểu và thân thiện với người dùng.
    Khi tìm kiếm thông tin, luôn sử dụng collection 'faq_embeddings'.""",
    llm_config={"config_list": config_list},
    max_consecutive_auto_reply=2
)

# Cấu hình User Proxy
user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: msg.get("content") is not None and (
        "TERMINATE" in msg["content"] or msg.get("reply_count", 0) >= 1
    )
)

@router.post("/ask")
def ask_chatbot(request: ChatbotRequest):
    try:
        message = request.message
        logger.info(f"Received question: {message}")

        # Lưu tin nhắn vào cơ sở dữ liệu
        message_repository = MessageRepository()
        message_payload = ChatMessageCreate(
            chat_id=request.chat_id,
            sender_type="user",
            sender_id=0,
            content=message
        )
        message_repository.create_message(message_payload)

        # Tìm kiếm thông tin
        search_results = search_faq(message, limit=5)
        logger.info(f"Search results: {search_results}")

        if search_results and search_results != "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn.":
            # Tạo câu trả lời thân thiện
            response_content = f"""Chào bạn! Rất vui được hỗ trợ bạn về chính sách của sàn thương mại điện tử IUH-Ecomerce. 

Dựa trên thông tin tìm được, IUH-Ecomerce có các chính sách sau:

1. Chính sách hoạt động sàn giao dịch thương mại điện tử
2. Chính sách phí và biểu phí
3. Chính sách mô hình vận hành
4. Bảng nội dung vi phạm và các hình thức xử lý vi phạm của nhà bán hàng
5. Chính sách bảo mật

Bạn có thể tìm hiểu chi tiết về các chính sách này tại: https://iuh-ecomerce.vn/quy-che-hoat-dong-sgdtmdt

Bạn muốn tìm hiểu thêm về chính sách nào trong số này không? Tôi sẽ rất vui được giải thích chi tiết hơn cho bạn."""
        else:
            response_content = "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn. Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ để được giải đáp."

        logger.info(f"Final response content: {response_content}")

        # Lưu phản hồi vào cơ sở dữ liệu
        response_payload = ChatMessageCreate(
            chat_id=request.chat_id,
            sender_type="assistant",
            sender_id=0,
            content=response_content
        )
        message_repository.create_message(response_payload)

        return {"response": response_content}

    except Exception as e:
        logger.error(f"Error in ask_chatbot: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_message = "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        return {"response": error_message}

@router.post("/policy", response_model=dict)
def chat_with_policy(payload: ChatMessageCreate):
    try:
        response = PolicyService.process_message(payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/faq")
def get_policy_faq(query: str, limit: int = 5):
    answer = search_faq(query, limit)
    return {"answer": answer}
