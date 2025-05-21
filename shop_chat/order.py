from fastapi import HTTPException, APIRouter, Depends
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopChatRequest
from repositories.orders import OrderRepository
from models.orders import OrderUpdate, OrderStatus
from db import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter(prefix="/shop/orders", tags=["Shop Orders"])

class OrderAgent:
    def __init__(self, db: Session):
        self.agent = AssistantAgent(
            name="order_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về quản lý đơn hàng cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Thông báo đơn hàng mới
            2. Hiển thị chi tiết đơn hàng
            3. Cập nhật trạng thái đơn hàng
            4. Hỗ trợ in phiếu giao hàng
            5. Theo dõi vận chuyển
            
            Bạn cần đảm bảo:
            - Xử lý đơn hàng nhanh chóng và chính xác
            - Cập nhật trạng thái đơn hàng kịp thời
            - Thông báo cho khách hàng về tiến độ đơn hàng
            - Hỗ trợ giải quyết vấn đề phát sinh
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )
        self.order_repository = OrderRepository(db)

    async def process_request(self, request: ShopChatRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "get":
                return await self._get_order(action["data"], request.shop_id)
            elif action["type"] == "update":
                return await self._update_order(action["data"], request.shop_id)
            elif action["type"] == "list":
                return await self._list_orders(action["data"], request.shop_id)
            elif action["type"] == "print":
                return await self._print_shipping_label(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in OrderAgent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _parse_action(self, response):
        try:
            data = json.loads(response)
            return {
                "type": data.get("action", "unknown"),
                "data": data.get("data", {})
            }
        except:
            return {"type": "unknown", "data": {}}

    async def _get_order(self, data, shop_id):
        try:
            order_id = data.get("order_id")
            if not order_id:
                raise HTTPException(status_code=400, detail="Order ID is required")
            
            # Get order details
            order = await self.order_repository.get_by_id(order_id)
            if not order or order.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return {
                "order": order,
                "items": await self.order_repository.get_order_items(order_id)
            }
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _update_order(self, data, shop_id):
        try:
            order_id = data.get("order_id")
            new_status = data.get("status")
            
            if not order_id or not new_status:
                raise HTTPException(status_code=400, detail="Order ID and status are required")
            
            # Verify order belongs to shop
            order = await self.order_repository.get_by_id(order_id)
            if not order or order.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Update order status
            update_data = OrderUpdate(status=new_status)
            updated_order = await self.order_repository.update(order_id, update_data)
            
            return {
                "message": "Trạng thái đơn hàng đã được cập nhật thành công",
                "order_id": order_id,
                "new_status": new_status
            }
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _list_orders(self, data, shop_id):
        try:
            status = data.get("status")
            page = data.get("page", 1)
            limit = data.get("limit", 10)
            
            # Get orders for shop with optional status filter
            orders = await self.order_repository.get_by_shop_id(
                shop_id=shop_id,
                status=status,
                page=page,
                limit=limit
            )
            
            return {
                "orders": orders,
                "page": page,
                "limit": limit,
                "total": await self.order_repository.count_by_shop_id(shop_id, status)
            }
        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _print_shipping_label(self, data, shop_id):
        try:
            order_id = data.get("order_id")
            if not order_id:
                raise HTTPException(status_code=400, detail="Order ID is required")
            
            # Verify order belongs to shop
            order = await self.order_repository.get_by_id(order_id)
            if not order or order.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Get shipping information
            shipping_info = await self.order_repository.get_shipping_info(order_id)
            
            # Generate shipping label (this would typically call a shipping service API)
            shipping_label = {
                "order_id": order_id,
                "shipping_address": shipping_info.address,
                "customer_name": shipping_info.customer_name,
                "phone": shipping_info.phone,
                "items": await self.order_repository.get_order_items(order_id)
            }
            
            return {
                "message": "Phiếu giao hàng đã được tạo",
                "shipping_label": shipping_label
            }
        except Exception as e:
            logger.error(f"Error printing shipping label: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

class Order:
    def __init__(self, db: Session = Depends(get_db)):
        self.agent = OrderAgent(db)
        self.order_repository = OrderRepository(db)

    async def create_order(self, order_data: dict) -> dict:
        """Create a new order"""
        try:
            order = await self.order_repository.create(order_data)
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_order(self, order_id: int) -> dict:
        """Get order details"""
        try:
            order = await self.order_repository.get_by_id(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            return order
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_order_status(self, order_id: int, status: OrderStatus) -> dict:
        """Update order status"""
        try:
            update_data = OrderUpdate(status=status)
            updated_order = await self.order_repository.update(order_id, update_data)
            return updated_order
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_total_orders(self) -> int:
        """Get total number of orders"""
        try:
            return await self.order_repository.count()
        except Exception as e:
            logger.error(f"Error getting total orders: {str(e)}")
            return 0

    async def process_request(self, request: dict) -> dict:
        """Process an order management request"""
        try:
            response = await self.agent.process_request(ShopChatRequest(**request))
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

# Add router endpoints
@router.get("/")
async def list_orders():
    """List all orders for a shop"""
    return {"message": "List orders endpoint"} 