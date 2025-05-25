import httpx
from fastapi import APIRouter, HTTPException, status
import asyncio
from autogen import AssistantAgent
from env import env


async def get_chat_history(chat_id: int, api_url: str, timeout: float = 10.0):
    url = f"{api_url}/api/customer/messages/messages/recent/{chat_id}?limit=5"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            messages = resp.json()
    except httpx.ReadTimeout:
        print(f"ERROR: Timeout when fetching chat history at {url}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"ERROR: HTTP error ({e.response.status_code}) when fetching chat history at {url}")
        return []
    except Exception as e:
        print(f"ERROR: Unexpected error when fetching chat history: {e}")
        return []

    # Convert to prompt format for LLM
    chat_history = []
    for msg in messages:
        # Lọc đúng một lượt mỗi bên (loại duplicate nếu có)
        if msg.get("sender_type") == "customer":
            chat_history.append({"role": "user", "content": msg.get("content", "")})
        elif msg.get("sender_type") in ["agent", "agent_response"]:
            chat_history.append({"role": "assistant", "content": msg.get("content", "")})
    return chat_history

config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": env.OPENAI_API_KEY,
        "api_type": "openai"
    }
]
prompt__message = """
Bạn là trợ lý AI của sàn thương mại điện tử IUH Ecommerce.
Đầu vào:
    Câu hỏi của khách hàng
    Toàn bộ lịch sử hội thoại giữa khách hàng và nhân viên chăm sóc khách hàng
Nhiệm vụ:
    Tổng hợp và diễn đạt lại tất cả các ý chính từ câu hỏi của khách hàng và lịch sử hội thoại thành một câu hỏi hoặc yêu cầu duy nhất, ngắn gọn, đầy đủ ý, phù hợp để chuyển tiếp cho agent khác (có thể là bộ phận chuyên môn, chatbot khác, hoặc hệ thống tự động xử lý).
Yêu cầu:
    Đầu ra chỉ gồm một câu hỏi hoặc yêu cầu duy nhất, không chứa bất kỳ thông tin, nhận xét, hay lời chào nào khác.
    Không để trống đầu ra. Nếu không hiểu đầu vào, hãy trả lại nguyên văn đầu vào.
    Không thêm, bớt hoặc suy diễn ngoài nội dung đã có.
    Đầu vào có thể bị sai chính tả, ngữ pháp hoặc không rõ ràng, bạn cần cố gắng hiểu và diễn đạt lại một cách chính xác nhất.
    Nếu lịch sử hội thoại có nhắc đến các thông tin quan trọng như: sản phẩm, chính sách, dịch vụ, mã đơn hàng, khuyến mãi,… hãy trích xuất và đưa vào trường "Info".
Định dạng đầu ra:
    Là một danh sách JSON (list) chứa các đối tượng với hai thuộc tính:
        reply: (string) Câu hỏi hoặc yêu cầu của khách hàng đã được tổng hợp
        Info: (object) Thông tin bổ sung đã trích xuất từ lịch sử hội thoại, gồm các trường phù hợp với ngữ cảnh: sản phẩm, dịch vụ, chính sách, mã đơn hàng, chương trình khuyến mãi, v.v.
Ví dụ đầu ra:
[
    {
        "reply": "Khách hàng muốn biết về chính sách đổi trả cho đơn hàng #12345?",
        "Info": {
            "Đơn_hàng": "#12345",
            "Chính_sách": "Đổi trả trong 7 ngày",
            "Sản_phẩm_đã_đề_cập": ["Áo thun nam"]
        }
    }
]
Hoặc:
[
    {
        "reply": "Khách hàng hỏi cách sử dụng mã khuyến mãi khi thanh toán?",
        "Info": {
            "Mã_khuyến_mãi": "IUHSALE2025"
        }
    }
]
Hoặc: 
[
    {
        "reply": "Khách hàng cần tư vấn chọn laptop phù hợp với thiết kế đồ họa?",
        "Info": {
            "Nhu_cầu": "Thiết kế đồ họa"
        }
    }
]


Ghi chú:
Có thể mở rộng Info tùy từng trường hợp, miễn là thông tin trích xuất nằm trong nội dung cuộc hội thoại.
Nếu không có thông tin nào nổi bật ngoài câu hỏi chính, Info có thể là {} hoặc không cần thêm trường.

"""

function_schema = {
    "name": "create_pronmpt",
    "description": "Create a prompt based on chat history",
    "parameters": {
        "type": "object",
        "properties": {
            "chat_history": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "enum": ["user", "assistant"]
                        },
                        "content": {
                            "type": "string"
                        }
                    },
                    "required": ["role", "content"]
                }
            }
        },
        "required": ["chat_history"]
    }
}

# Agent tạo prompt từ lịch sử hội thoại và câu hỏi của khách hàng
prompt_agent = AssistantAgent(
    name="prompt_agent",
    description="Agent to create prompt",
    system_message=prompt__message,
    llm_config={"config_list": config_list}
)
router = APIRouter(prefix="/manager", tags=["Manager"])
@router.post("/chatbot/reply")
async def chatbot_reply(message, chat_id = 0, api_url: str = "http://localhost:8000"):
    chat_history = await get_chat_history(chat_id, api_url)
    # Ghép lịch sử và message hiện tại vào chat_history
    full_chat_history = chat_history.copy() if chat_history else []
    # Bổ sung câu hỏi mới nhất
    full_chat_history.append({"role": "user", "content": message})

    # Gọi hàm với messages và function_call đúng tên
    reply = prompt_agent.generate_reply(
        messages=[
            {"role": "user", "content": str(full_chat_history)}
        ]
    )
    print("❎❎❎✅✅✅➡️➡️💣💣💣🤣🤣Reply from agent:", reply)
    
    # Extract the reply content from the response
    if isinstance(reply, dict):
        if 'content' in reply:
            return reply['content']
        elif 'reply' in reply:
            return reply['reply']
        else:
            return str(reply)
    return str(reply)


output_messgae = """
Bạn là một trợ lý AI của sàn thương mại điện tử IUH Ecommerce.
Bạn sẽ nhận được đầu vào là câu trả lời khách hàng cho câu hỏi của khách hàng
nhiệm vụ của bạn là parsing lại câu trả lời cho đẹp hơn
Hãy dùng latex để định dạng câu trả lời, Mỗi khi cần xuống dòng hãy dùng \n, mỗi khi cần tab dùng \t, tuyệt đối không dùng latext khác
"""

OutputAgent  = AssistantAgent(
    name="OutputAgent",
    description="Agent to create output",
    system_message=output_messgae,
    llm_config={"config_list": config_list}
)

@router.post("/chatbot/output")
async def chatbot_output(message ):

    reply = OutputAgent.generate_reply(
        messages=[
            {"role": "user", "content": message}
        ]
    )
    print("❎❎❎✅✅✅➡️➡️💣💣💣🤣🤣Reply from agent:", reply)
    return reply





# async def main():
#     chat_id = 107
#     api_url = "http://localhost:8000"
#     history_chat = await get_chat_history(chat_id, api_url)
#     print("Chat history:", history_chat)

#     if not history_chat:
#         print("No chat history found, aborting.")
#         return

#     request = ChatbotRequest(
#         chat_id=85,
#         message="sản phẩm đó có phug hợp với trẻ em không",
#         user_id=1,
#         shop_id=0
#     )
#     result = chatbot_reply(request, history_chat)
#     print("Chatbot reply:", result)

# if __name__ == "__main__":
#     asyncio.run(main())
