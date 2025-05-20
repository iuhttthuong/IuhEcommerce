from typing import Dict, Any, Optional
from .base import BaseShopAgent, ShopChatRequest, ShopChatResponse
from .product_management import ProductManagementAgent
from .inventory import InventoryAgent
from .order import OrderAgent
from .marketing import MarketingAgent
from .finance import FinanceAgent
from .analytics import AnalyticsAgent
from .customer_service import CustomerServiceAgent
from .policy import PolicyAgent

class ShopOrchestrator(BaseShopAgent):
    def __init__(self, shop_id: int):
        super().__init__(shop_id)
        self.agents = {
            "product": ProductManagementAgent(shop_id),
            "inventory": InventoryAgent(shop_id),
            "order": OrderAgent(shop_id),
            "marketing": MarketingAgent(shop_id),
            "finance": FinanceAgent(shop_id),
            "analytics": AnalyticsAgent(shop_id),
            "customer_service": CustomerServiceAgent(shop_id),
            "policy": PolicyAgent(shop_id)
        }

    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
        # Analyze the message to determine which agent should handle it
        intent = self._analyze_intent(request.message)
        
        if intent in self.agents:
            # Route to specialized agent
            return await self.agents[intent].process(request)
        else:
            # Default response if no specific intent is detected
            return self._create_response(
                "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại với một yêu cầu cụ thể hơn.",
                {"intent": "unknown"}
            )

    def _analyze_intent(self, message: str) -> str:
        """
        Analyze the message to determine which agent should handle it
        Returns the name of the appropriate agent
        """
        message = message.lower()
        
        # Product management intent
        if any(word in message for word in ["sản phẩm", "thêm sản phẩm", "cập nhật sản phẩm", "xóa sản phẩm"]):
            return "product"
            
        # Inventory intent
        if any(word in message for word in ["tồn kho", "kiểm kho", "nhập kho", "xuất kho"]):
            return "inventory"
            
        # Order intent
        if any(word in message for word in ["đơn hàng", "xác nhận đơn", "hủy đơn", "giao hàng"]):
            return "order"
            
        # Marketing intent
        if any(word in message for word in ["khuyến mãi", "giảm giá", "quảng cáo", "marketing"]):
            return "marketing"
            
        # Finance intent
        if any(word in message for word in ["doanh thu", "chi phí", "thanh toán", "tài chính"]):
            return "finance"
            
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