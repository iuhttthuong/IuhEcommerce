from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .product_management import ProductManagement, ProductManagementAgent
from .inventory import Inventory
from .marketing import Marketing
from .customer_service import CustomerService
from .analytics import Analytics
from .chat_repository import ChatRepository
from models.shops import Shop
from models.products import Product, ProductCreate
from models.orders import Order as OrderModel, OrderCreate
from models.customers import Customer, CustomerCreate
from models.promotions import PromotionCreate
from .schemas import AnalyticsRequest
from autogen import ConversableAgent
from env import env
from db import get_db
import json
from loguru import logger
from .base import ShopChatRequest, ShopChatResponse

class ShopManager:
    def __init__(self, db: Session = Depends(get_db)):
        self.product_mgmt = ProductManagement(db)
        self.inventory = Inventory(db)
        self.marketing = Marketing(db)
        self.customer_service = CustomerService(db)
        self.analytics = Analytics(db)
        self.chat_repo = ChatRepository(db)
        
        # Khởi tạo ConversableAgent cho chat
        config_list = [
            {
                "model": "gemini-2.0-flash",
                "api_key": env.GEMINI_API_KEY,
                "api_type": "google"
            }
        ]
        
        self.chat_agent = ConversableAgent(
            name="shop_manager",
            system_message="""Bạn là một trợ lý AI thông minh làm việc cho shop trên sàn thương mại điện tử IUH-Ecomerce
            Bạn sẽ nhận đầu vào câu hỏi của chủ shop về quản lý shop
            Nhiệm vụ của bạn là trả lời câu hỏi của chủ shop một cách chính xác và đầy đủ nhất có thể
            Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin

            Khi nhận được câu hỏi, hãy phân tích và trả về JSON với agent phù hợp:
            - Nếu là câu hỏi về danh sách sản phẩm (ví dụ: "tôi có những sản phẩm nào", "danh sách sản phẩm", "liệt kê sản phẩm") => Sử dụng ProductManagementAgent
            - Nếu là câu hỏi về thêm/sửa/xóa sản phẩm => Sử dụng ProductManagementAgent
            - Nếu là câu hỏi về tồn kho => Sử dụng InventoryAgent
            - Nếu là câu hỏi về khách hàng => Sử dụng CustomerServiceAgent
            - Nếu là câu hỏi về marketing => Sử dụng MarketingAgent
            - Nếu là câu hỏi về báo cáo => Sử dụng AnalyticsAgent
            - Nếu là câu hỏi về chính sách shop => Sử dụng PolicyAgent

            Hãy trả về mô tả truy vấn dưới dạng JSON:
            ```json
            {
                "agent": "ProductManagementAgent" | "InventoryAgent" | "MarketingAgent" | "CustomerServiceAgent" | "AnalyticsAgent" | "PolicyAgent" | "MySelf",
                "query": String
            }
            ```

            Với Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin:
            - ProductManagementAgent: Quản lý sản phẩm (thêm, sửa, xóa, liệt kê)
            - InventoryAgent: Quản lý kho hàng
            - MarketingAgent: Quản lý marketing và khuyến mãi
            - CustomerServiceAgent: Quản lý dịch vụ khách hàng
            - AnalyticsAgent: Phân tích dữ liệu và báo cáo
            - PolicyAgent: Quản lý chính sách shop
            - MySelf: Trả lời câu hỏi chung

            Lưu ý quan trọng:
            1. KHÔNG yêu cầu người dùng cung cấp thông tin đăng nhập hoặc tên shop
            2. KHÔNG hướng dẫn người dùng đăng nhập vào trang quản trị
            3. Khi nhận được yêu cầu liệt kê sản phẩm:
               - LUÔN sử dụng ProductManagementAgent
               - KHÔNG trả về JSON trong câu trả lời
               - KHÔNG yêu cầu ID người bán
               - Chỉ trả về JSON khi cần chọn agent
            4. Nếu không có sản phẩm nào, trả về thông báo "Chưa có sản phẩm nào trong cửa hàng của bạn"
            5. KHÔNG trả về JSON trong câu trả lời cuối cùng, chỉ trả về JSON khi cần chọn agent
            """,    
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

    async def process_chat_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[DEBUG] Context at start: {context}")
        try:
            # Luôn đảm bảo shop_id là số nguyên nếu có
            if 'shop_id' in context and context['shop_id']:
                context['shop_id'] = int(context['shop_id'])
            else:
                print("[DEBUG] Không có shop_id trong context, trả về hướng dẫn.")
                return {
                    "response": "Bạn vui lòng cung cấp shop_id hoặc thông tin nhận diện shop để tôi có thể lấy danh sách sản phẩm.",
                    "agent": "ProductManagementAgent",
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            # Gọi agent
            chat_response = await self.chat_agent.a_generate_reply(
                messages=[{"role": "user", "content": message}]
            )
            content = chat_response.get('content', '')
            print(f"[DEBUG] Chat agent content: {content}")
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    response = json.loads(json_str)
                    print(f"[DEBUG] Parsed chat agent response: {response}")
                else:
                    print("[DEBUG] No JSON found in chat agent response")
                    response = {
                        "agent": "MySelf",
                        "query": message
                    }
            except Exception as e:
                print(f"[DEBUG] Error parsing JSON: {e}")
                response = {
                    "agent": "MySelf",
                    "query": message
                }
            agent = response.get("agent")
            query = response.get("query")
            print(f"[DEBUG] Selected agent: {agent}, query: {query}")
            # LUÔN gọi _handle_list_products nếu agent là ProductManagementAgent và có shop_id
            if agent == "ProductManagementAgent":
                print("[DEBUG] Đã vào nhánh ProductManagementAgent, gọi _handle_list_products")
                product_agent = ProductManagementAgent(shop_id=context['shop_id'], db=self.db)
                result = await product_agent._handle_list_products(ShopChatRequest(message=query, context=context))
                await self.chat_repo.save_message(message, result.message, context)
                print(f"[DEBUG] Đã trả về kết quả liệt kê sản phẩm: {result.message}")
                return {
                    "response": result.message,
                    "agent": "ProductManagementAgent",
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            # Các agent khác giữ nguyên
            elif agent == "InventoryAgent":
                result = await self.inventory.process_request({"message": query, "context": context})
            elif agent == "MarketingAgent":
                result = await self.marketing.process_request({"message": query, "context": context})
            elif agent == "CustomerServiceAgent":
                result = await self.customer_service.process_request({"message": query, "context": context})
            elif agent == "AnalyticsAgent":
                result = await self.analytics.process_request({"message": query, "context": context})
            elif agent == "PolicyAgent":
                result = {
                    "message": "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                    "type": "error"
                }
            elif agent == "MySelf":
                result = {
                    "message": "Xin chào! Tôi là trợ lý AI quản lý shop của IUH-Ecomerce. Tôi có thể giúp gì cho bạn?",
                    "type": "greeting"
                }
            else:
                result = {
                    "message": "Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                    "type": "error"
                }
            # Lưu tin nhắn vào database
            await self.chat_repo.save_message(message, result.get("message", str(result)), context)
            # Get the chat session after saving the message
            session_id = context.get('session_id')
            if session_id:
                chat = self.chat_repo.get_session(session_id, context.get('shop_id'))
                return {
                    "chat_id": chat.chat_id,
                    "shop_id": chat.shop_id,
                    "customer_id": chat.customer_id,
                    "status": chat.status,
                    "last_message_at": chat.last_message_at,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create chat session")

        except Exception as e:
            logger.error(f"Error in process_chat_message: {str(e)}")
            logger.exception("Full traceback:")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        return await self.product_mgmt.create_product(product_data)

    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Product:
        """Update product information"""
        return await self.product_mgmt.update_product(product_id, product_data)

    async def get_product(self, product_id: int) -> Product:
        """Get product details"""
        return await self.product_mgmt.get_product(product_id)

    async def list_products(self, filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        """List all products with optional filters"""
        return await self.product_mgmt.list_products(filters)

    # async def create_order(self, order_data: OrderCreate) -> OrderModel:
    #     """Create a new order"""
    #     # Check inventory
    #     for item in order_data.items:
    #         if not await self.inventory.check_stock(item.product_id, item.quantity):
    #             raise ValueError(f"Insufficient stock for product {item.product_id}")
        
    #     # Create order
    #     order = await self.order_mgmt.create_order(order_data)
        
    #     # Update inventory
    #     for item in order_data.items:
    #         await self.inventory.update_stock(item.product_id, -item.quantity)
        
    #     return order

    # async def get_order(self, order_id: int) -> OrderModel:
    #     """Get order details"""
    #     return await self.order_mgmt.get_order(order_id)

    async def update_order_status(self, order_id: int, status: str) -> OrderModel:
        """Update order status"""
        return await self.order_mgmt.update_order_status(order_id, status)

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer"""
        return await self.customer_service.create_customer(customer_data)

    async def get_customer(self, customer_id: int) -> Customer:
        """Get customer details"""
        return await self.customer_service.get_customer(customer_id)

    async def create_marketing_campaign(self, campaign_data: PromotionCreate) -> Dict[str, Any]:
        """Create a new marketing campaign"""
        return await self.marketing.create_campaign(campaign_data)

    async def get_analytics(self, request: AnalyticsRequest) -> Dict[str, Any]:
        """Get shop analytics"""
        return await self.analytics.get_analytics(request)

    async def get_shop_summary(self) -> Dict[str, Any]:
        """Get shop summary including key metrics"""
        return {
            "total_products": await self.product_mgmt.get_total_products(),
            "total_customers": await self.customer_service.get_total_customers(),
            "inventory_value": await self.inventory.get_total_inventory_value()
        } 