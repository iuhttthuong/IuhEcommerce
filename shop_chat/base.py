from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json
from autogen import AssistantAgent, ConversableAgent
from env import env
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

# Base configuration for shop agents
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]

class ShopChatRequest(BaseModel):
    shop_id: int
    message: str
    user_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class ShopChatResponse(BaseModel):
    response: str
    agent: str
    context: Optional[Dict[str, Any]] = None
    timestamp: str = str(datetime.utcnow())

class BaseShopAgent(ABC):
    def __init__(self, shop_id: int):
        self.shop_id = shop_id
        self.name = self.__class__.__name__

    @abstractmethod
    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
        pass

    def _create_response(self, response: str, context: Optional[Dict[str, Any]] = None) -> ShopChatResponse:
        return ShopChatResponse(
            response=response,
            agent=self.name,
            context=context
        )

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

async def process_shop_chat(request: ShopChatRequest) -> ShopChatResponse:
    chat = await ShopManager.a_generate_reply(
        messages=[{"role": "user", "content": request.message}])
    print(f"Chat: {chat}")
    
    # Extract JSON from markdown code block if present
    content = chat.get("content", "")
    if content.startswith("```json") and content.endswith("```"):
        try:
            # Remove markdown code block markers and parse JSON
            json_str = content.replace("```json", "").replace("```", "").strip()
            parsed_response = json.loads(json_str)
            return ShopChatResponse(
                response=parsed_response.get("query", "Xin lỗi, tôi không thể xử lý yêu cầu của bạn."),
                agent=parsed_response.get("agent", "ShopManager"),
                context=request.context
            )
        except json.JSONDecodeError:
            pass
    
    # Fallback to direct content if not JSON or parsing fails
    return ShopChatResponse(
        response=content,
        agent="ShopManager",
        context=request.context
    )

async def get_shop_info(query):
    chat = await ShopManager.a_generate_reply(
        messages=[{"role": "user", "content": query}])
    print(f"Chat: {chat}")
    content = chat.get("content", "")
    
    # Extract JSON from markdown code block if present
    if content.startswith("```json") and content.endswith("```"):
        try:
            json_str = content.replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return {"content": content} 