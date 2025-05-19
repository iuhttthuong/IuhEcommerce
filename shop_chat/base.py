from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json
from autogen import AssistantAgent, ConversableAgent
from env import env

# Base configuration for shop agents
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]

class ShopRequest(BaseModel):
    shop_id: int
    message: str
    context: dict = None

# Base shop agent configuration
ShopManager = ConversableAgent(
    name="shop_manager",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho sàn thương mại điện tử IUH-Ecomerce
    Bạn sẽ nhận đầu vào câu hỏi của người bán hàng về quản lý shop trên sàn
    Nhiệm vụ của bạn là trả lời câu hỏi và hỗ trợ người bán một cách chính xác và đầy đủ nhất có thể
    Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin
    Hãy trả về mô tả truy vấn dưới dạng JSON:
    {
        "agent": "ProductManagementAgent" | "InventoryAgent" | "OrderAgent" | "MarketingAgent" | "AnalyticsAgent" | "FinanceAgent" | "PolicyAgent" | "CustomerServiceAgent",
        "query": String
    }
    Với Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin:
        ProductManagementAgent: Quản lý sản phẩm (đăng, cập nhật, xóa)
        InventoryAgent: Quản lý tồn kho
        OrderAgent: Xử lý đơn hàng
        MarketingAgent: Quản lý khuyến mãi và marketing
        AnalyticsAgent: Phân tích và báo cáo
        FinanceAgent: Quản lý tài chính và thanh toán
        PolicyAgent: Hỗ trợ chính sách và quy định
        CustomerServiceAgent: Quản lý tương tác khách hàng
    """,
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)

async def get_shop_info(query):
    chat = await ShopManager.a_generate_reply(
        messages=[{"role": "user", "content": query}])
    print(f"Chat: {chat}")
    response = json.loads(chat)
    return response 