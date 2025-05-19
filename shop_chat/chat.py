from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from autogen import AssistantAgent, ConversableAgent
from env import env
import json

router = APIRouter(prefix="/shop/chat", tags=["Shop Chat"])

# Configuration for shop chat agents
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
    timestamp: datetime = datetime.now()
    context: Optional[Dict[str, Any]] = None

# Shop Chat Manager Agent
ShopChatManager = ConversableAgent(
    name="shop_chat_manager",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho sàn thương mại điện tử IUH-Ecomerce
    Bạn sẽ nhận đầu vào câu hỏi của người bán hàng về quản lý shop trên sàn
    Nhiệm vụ của bạn là phân tích câu hỏi và điều hướng đến agent phù hợp để xử lý
    Hãy trả về mô tả truy vấn dưới dạng JSON:
    {
        "agent": "ProductManagementAgent" | "InventoryAgent" | "OrderAgent" | "MarketingAgent" | 
                "AnalyticsAgent" | "FinanceAgent" | "PolicyAgent" | "CustomerServiceAgent",
        "query": String,
        "intent": String,
        "entities": Dict
    }
    Với:
    - agent: Tên của agent phù hợp để xử lý câu hỏi
    - query: Câu hỏi cần xử lý
    - intent: Ý định của người dùng (ví dụ: "check_inventory", "update_product", "view_orders")
    - entities: Các thực thể được trích xuất từ câu hỏi (ví dụ: product_id, order_id)
    """,
    llm_config={"config_list": config_list},
    human_input_mode="NEVER"
)

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

async def process_shop_chat(request: ShopChatRequest) -> ShopChatResponse:
    try:
        # Get initial analysis from manager
        manager_response = await ShopChatManager.a_generate_reply(
            messages=[{"role": "user", "content": request.message}]
        )
        analysis = json.loads(manager_response)
        
        # Route to appropriate agent
        agent = analysis["agent"]
        query = analysis["query"]
        
        if agent == "ProductManagementAgent":
            response = await product_agent.a_generate_reply(
                messages=[{"role": "user", "content": query}]
            )
        elif agent == "InventoryAgent":
            response = await inventory_agent.a_generate_reply(
                messages=[{"role": "user", "content": query}]
            )
        elif agent == "OrderAgent":
            response = await order_agent.a_generate_reply(
                messages=[{"role": "user", "content": query}]
            )
        else:
            # Default to manager if no specific agent matches
            response = await ShopChatManager.a_generate_reply(
                messages=[{"role": "user", "content": query}]
            )
        
        return ShopChatResponse(
            response=response,
            agent=agent,
            context={
                "intent": analysis.get("intent"),
                "entities": analysis.get("entities", {})
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

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