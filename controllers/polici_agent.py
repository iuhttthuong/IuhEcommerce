import asyncio
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

# Lấy cấu hình model từ môi trường
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": env.OPENAI_API_KEY
    }
]



assistant = ConversableAgent(
    name="Assistant",
    system_message="Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecomerce"
    "Bạn sẽ nhận đầu vào câu hỏi của người dùng về các chính sách của sàn thương mại điện tử IUH-Ecomerce"
    "Nhiệm vụ của bạn là tìm kiếm thông tin trong cơ sở dữ liệu và trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể"
    "Đầu ra dưới dạng string  là 1 đoạn văn duy nhất, không thêm ký tự đặc biệt, thêm dấu câu nếu cần",
    llm_config={"config_list": config_list},
    max_consecutive_auto_reply=2
)

user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and (
        "TERMINATE" in msg["content"] or msg.get("reply_count", 0) >= 0
    ),human_input_mode="NEVER",
)


router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

def get_fqa(payload: str, collection_name: str = "poli_embeddings", limit: int = 1):
    """
    Tìm kiếm sản phẩm trong cơ sở dữ liệu.
    """

    search_result = search(payload, collection_name=collection_name, limit=1)
    print(f"S❎❎❎❎❎earch result: {search_result}")
    if not search_result:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin")
    with Session() as session:
        fqa = session.query(FQA).filter(FQA.id == search_result[0]).first()
        print(f"FQA: {fqa.answer}")
        if not fqa:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin")
    return fqa.answer


@router.post("/ask")
def ask_chatbot(request: str):
    try:
        message = request

        # # Lưu tin nhắn vào cơ sở dữ liệu
        # message_repository = MessageRepository()
        # message_payload = CreateMessagePayload(
        #     chat_id=request.chat_id,
        #     role="user",
        #     content=message
        # )
        # message_repository.create(message_payload)

        # Tạo câu hỏi cho agent
        # print(search(request))
        # get_fqa(request, collection_name="poli_embeddings", limit=1)
        question = f"Người dùng hỏi: {message}"

        register_function(
            get_fqa,
            caller=assistant,  
            executor=user_proxy,  
            name="search",  
            description="A simple search function", 
        )
        chat_result = user_proxy.initiate_chat(
            assistant,
            message=question,
            function_call={"name": "search"},
            function_args={"payload": message, "collection_name": "poli_embeddings", "limit": 1},
            auto_reply=True,
            silent=True  # Ẩn tin nhắn này trong lịch sử chat
        )
        print(f"Response from assistant: {chat_result.summary}")
        # Lưu phản hồi vào cơ sở dữ liệu
        # response_payload = CreateMessagePayload(
        #     chat_id=request.chat_id,
        #     role="assistant",
        #     content=chat_result.summary
        # )
        # message_repository.create(response_payload)

        return chat_result.summary

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Đã xảy ra lỗi khi xử lý yêu cầu")



# test
# asyncio.run(ask_chatbot("hãy nói về chính sách bao hành của IUH-Ecommerce"))
# ask_chatbot("hãy nói về chính sách bao hành của IUH-Ecommerce")