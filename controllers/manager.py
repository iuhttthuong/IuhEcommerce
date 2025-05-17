from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import traceback
from autogen import ConversableAgent
from env import env

from controllers.qdrant_agent import chatbot_endpoint as product_agent
from controllers.polici_agent import ask_chatbot as policy_agent
from controllers.search import search
from repositories.message import MessageRepository
from models.message import CreateMessagePayload

router = APIRouter(prefix="/manager", tags=["Chatbot"])

# Cấu hình model từ môi trường
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": env.OPENAI_API_KEY
    }
]

class ChatbotRequest(BaseModel):
    chat_id: int
    message: str


Manager = ConversableAgent(
    name="manager",
    system_message=(
        "Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecomerce. "
        "Bạn sẽ nhận đầu vào câu hỏi của người dùng về sàn thương mại điện tử IUH-Ecomerce. "
        "Nhiệm vụ của bạn là trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể. "
        "Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin. "
        "Hãy trả về mô tả truy vấn Qdrant dưới dạng JSON duy nhất, KHÔNG kèm giải thích: "
        '{"agent": "ProductAgent" | "PoliciAgent" | "MySelf" | "TransactionAgent", "query": "string"}'
    ),
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)

Iuh = ConversableAgent(
    name="myself",
    system_message=(
        "Bạn là một trợ lý AI thông minh làm việc cho một sàn thương mại điện tử IUH-Ecomerce. "
        "Bạn sẽ nhận đầu vào câu hỏi của người dùng về sàn thương mại điện tử IUH-Ecomerce. "
        "Nhiệm vụ của bạn là trả lời câu hỏi của người dùng một cách chính xác và đầy đủ nhất có thể. "
        "Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin. "
        "Hãy trả về mô tả truy vấn Qdrant dưới dạng string duy nhất, KHÔNG kèm giải thích: "
    ),
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)

async def get_product_info(query: str):
    chat = await Manager.a_generate_reply(
        messages=[{"role": "user", "content": query}]
    )
    print(f"Raw chat response: {chat} (type: {type(chat)})")

    # Nếu trả về dict có key 'content' thì lấy ra, nếu trả về string thì dùng luôn
    if isinstance(chat, dict) and "content" in chat:
        content = chat["content"]
    else:
        content = chat

    if not content or not isinstance(content, str):
        raise ValueError("Empty or invalid response from agent")

    try:
        response = json.loads(content)
    except json.JSONDecodeError:
        print(f"Response is not valid JSON: {content}")
        raise ValueError("Response is not valid JSON")

    return response


async def call_agent(agent: str, request: ChatbotRequest):
    if agent == "ProductAgent":
        result = await product_agent(request)
        return result
    elif agent == "PoliciAgent":
        result = policy_agent(request)
        # giả sử policy_agent trả về dict có key 'response'
        return result.get("response") if isinstance(result, dict) else result
    elif agent == "MySelf":
        result = await Iuh.a_generate_reply(
            messages=[{"role": "user", "content": request.message}]
        )
        return result
    elif agent == "TransactionAgent":
        result = search(request.message)
        return result
    else:
        raise ValueError(f"Unknown agent: {agent}")


@router.post("/ask")
async def ask_chatbot(request: ChatbotRequest):
    try:
        print(f"Received message: {request.message}")

        # Lưu tin nhắn vào DB
        message_repository = MessageRepository()
        message_payload = CreateMessagePayload(
            chat_id=request.chat_id,
            role="user",
            content=request.message
        )
        new_mess = message_repository.create(message_payload)

        # Tạo câu hỏi
        question = f"Người dùng hỏi: {request.message}"
        print(f"Querying Manager with question: {question}")

        # Gọi hàm lấy agent + query JSON
        response = await get_product_info(question)
        print(f"Parsed JSON response from Manager: {response}")

        
        result = await call_agent(response["agent"], request)
        print(f"Final result from agent {response['agent']}: {result}")

        ## lưu phản hồi vào DB
        response_payload = CreateMessagePayload(
            chat_id=request.chat_id,
            role="assistant",
            content=result
        )
        message_repository.create(response_payload)

        return {
            "message": result,
            "agent": response["agent"],
            "message_id": new_mess.id,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e) or "Đã xảy ra lỗi khi xử lý yêu cầu.")

async def test():
    rs = await ask_chatbot(
        ChatbotRequest(
            chat_id=1,
            message="hãy nói về chính sách bao hành của IUH-Ecommerce"
        )
    )
    print(rs)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
    