from typing import Dict, Any, Optional
from .base import BaseShopAgent, ShopRequest, ShopChatRequest
from .product_management import ProductManagementAgent
from .inventory import InventoryAgent
from .marketing import MarketingAgent
from .analytics import AnalyticsAgent
from .customer_service import CustomerServiceAgent
from .policy import PolicyAgent

class ShopOrchestrator(BaseShopAgent):
    def __init__(self, shop_id: int):
        super().__init__(shop_id)
        self.agents = {
            "product": ProductManagementAgent(shop_id),
            "inventory": InventoryAgent(shop_id),
            "marketing": MarketingAgent(shop_id),
            "analytics": AnalyticsAgent(shop_id),
            "customer_service": CustomerServiceAgent(shop_id),
            "policy": PolicyAgent(shop_id)
        }

    async def process(self, request: ShopChatRequest) -> Dict[str, Any]:
        intent = self._analyze_intent(request.message)
        if intent in self.agents:
            # Convert ShopChatRequest to ShopRequest for agent
            shop_request = ShopRequest(
                message=request.message,
                chat_id=request.chat_id,
                shop_id=request.shop_id,
                user_id=request.user_id,
                context=request.context,
                entities=request.entities,
                agent_messages=request.agent_messages,
                filters=request.filters
            )
            return await self.agents[intent].process(shop_request)
        else:
            return self._create_response(
                "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại với một yêu cầu cụ thể hơn.",
                {"intent": "unknown"}
            )

    def _analyze_intent(self, message: str) -> str:
        message = message.lower()
        # Product management intent
        if any(word in message for word in ["sản phẩm", "thêm sản phẩm", "cập nhật sản phẩm", "xóa sản phẩm"]):
            return "product"
        # Inventory intent
        if any(word in message for word in ["tồn kho", "kiểm kho", "nhập kho", "xuất kho"]):
            return "inventory"
        # Marketing intent
        if any(word in message for word in ["khuyến mãi", "giảm giá", "quảng cáo", "marketing"]):
            return "marketing"
        # Analytics intent
        if any(word in message for word in ["báo cáo", "thống kê", "phân tích", "dashboard"]):
            return "analytics"
        # Customer service intent
        if any(word in message for word in ["khách hàng", "phản hồi", "đánh giá", "khiếu nại"]):
            return "customer_service"
        # Policy intent
        if any(word in message for word in ["chính sách", "quy định", "điều khoản", "hướng dẫn"]):
            return "policy"
        return "unknown" 