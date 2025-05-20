from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from autogen import AssistantAgent, ConversableAgent
from env import env
import json
from .base import ShopChatRequest, ShopChatResponse, process_shop_chat

router = APIRouter(prefix="/shop/chat", tags=["Shop Chat"])

# Configuration for shop chat agents
config_list = [
    {
        "model": "gemini-2.0-flash",
        "api_key": env.GEMINI_API_KEY,
        "api_type": "google"
    }
]

# Specialized Shop Agents
class ProductManagementAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="product_management_agent",
            system_message="""Bạn là agent chuyên xử lý các câu hỏi về quản lý sản phẩm trong shop.
            Bạn có thể:
            - Tư vấn về cách đăng sản phẩm
            - Hướng dẫn cập nhật thông tin sản phẩm
            - Giải thích về chính sách sản phẩm
            - Tư vấn về giá và khuyến mãi
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

class InventoryAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="inventory_agent",
            system_message="""Bạn là agent chuyên xử lý các câu hỏi về quản lý tồn kho.
            Bạn có thể:
            - Kiểm tra số lượng tồn kho
            - Tư vấn về quản lý tồn kho
            - Cảnh báo khi hàng sắp hết
            - Hướng dẫn nhập hàng
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

class OrderAgent(ConversableAgent):
    def __init__(self):
        super().__init__(
            name="order_agent",
            system_message="""Bạn là agent chuyên xử lý các câu hỏi về đơn hàng.
            Bạn có thể:
            - Kiểm tra trạng thái đơn hàng
            - Hướng dẫn xử lý đơn hàng
            - Tư vấn về vận chuyển
            - Giải quyết vấn đề đơn hàng
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

# Initialize agents
product_agent = ProductManagementAgent()
inventory_agent = InventoryAgent()
order_agent = OrderAgent()

@router.post("/ask", response_model=ShopChatResponse)
async def ask_shop_chat(request: ShopChatRequest):
    """
    Endpoint to handle shop-related chat queries
    """
    return await process_shop_chat(request)

@router.get("/agents")
async def list_available_agents():
    """
    List all available shop chat agents and their capabilities
    """
    return {
        "agents": [
            {
                "name": "ProductManagementAgent",
                "capabilities": [
                    "Product listing and updates",
                    "Product policy guidance",
                    "Pricing and promotion advice"
                ]
            },
            {
                "name": "InventoryAgent",
                "capabilities": [
                    "Stock level checking",
                    "Inventory management advice",
                    "Low stock alerts",
                    "Stock replenishment guidance"
                ]
            },
            {
                "name": "OrderAgent",
                "capabilities": [
                    "Order status checking",
                    "Order processing guidance",
                    "Shipping advice",
                    "Order issue resolution"
                ]
            }
        ]
    } 