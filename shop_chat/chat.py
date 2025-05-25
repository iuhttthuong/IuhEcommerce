from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json
from autogen import AssistantAgent, ConversableAgent
from env import env
from .base import ShopRequest, ChatMessageRequest, process_shop_chat
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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

@router.post("/query")
async def query_shop_chat(request: ChatMessageRequest):
    try:
        # Convert to ShopRequest format
        shop_request = ShopRequest(
            message=request.content,
            chat_id=request.chat_id,
            shop_id=request.sender_id if request.sender_type == "shop" else None,
            user_id=request.sender_id if request.sender_type == "user" else None,
            context=request.message_metadata if request.message_metadata else {},
            entities={},
            agent_messages=[],
            filters={}
        )
        response = await process_shop_chat(shop_request)
        return response
    except Exception as e:
        logger.error(f"Error in query_shop_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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