from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest, BaseShopAgent, ShopAgentRequest, ShopAgentResponse
from repositories.promotions import PromotionRepository
from models.promotions import PromotionCreate, PromotionUpdate, PromotionType
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/shop/marketing", tags=["Shop Marketing"])

class MarketingAgent(BaseShopAgent):
    def __init__(self, shop_id: int):
        super().__init__(shop_id, "marketing")
        self.promotion_repository = PromotionRepository()

    async def process(self, request: ShopAgentRequest) -> ShopAgentResponse:
        message = request.message.lower()
        
        if "tạo khuyến mãi" in message or "thêm khuyến mãi" in message:
            return await self._handle_create_promotion(request)
        elif "danh sách khuyến mãi" in message:
            return await self._handle_list_promotions(request)
        elif "cập nhật khuyến mãi" in message:
            return await self._handle_update_promotion(request)
        elif "xóa khuyến mãi" in message:
            return await self._handle_delete_promotion(request)
        else:
            return self._create_response(
                "Tôi có thể giúp bạn quản lý các chương trình khuyến mãi. "
                "Bạn có thể:\n"
                "- Tạo khuyến mãi mới\n"
                "- Xem danh sách khuyến mãi\n"
                "- Cập nhật thông tin khuyến mãi\n"
                "- Xóa khuyến mãi\n"
                "Bạn muốn thực hiện thao tác nào?"
            )

    async def _handle_create_promotion(self, request: ShopAgentRequest) -> ShopAgentResponse:
        return self._create_response(
            "Để tạo khuyến mãi mới, vui lòng cung cấp các thông tin sau:\n"
            "1. Tên chương trình khuyến mãi\n"
            "2. Mã khuyến mãi\n"
            "3. Loại khuyến mãi (phần trăm, số tiền cố định, miễn phí vận chuyển)\n"
            "4. Giá trị khuyến mãi\n"
            "5. Thời gian bắt đầu và kết thúc\n"
            "6. Giá trị đơn hàng tối thiểu (nếu có)\n"
            "7. Giảm giá tối đa (nếu có)\n"
            "8. Giới hạn số lần sử dụng (nếu có)\n"
            "9. Áp dụng cho sản phẩm/category cụ thể (nếu có)\n"
            "10. Mô tả chi tiết"
        )

    async def _handle_list_promotions(self, request: ShopAgentRequest) -> ShopAgentResponse:
        return self._create_response(
            "Để xem danh sách khuyến mãi, vui lòng chọn:\n"
            "1. Xem tất cả khuyến mãi\n"
            "2. Xem khuyến mãi đang hoạt động\n"
            "3. Xem khuyến mãi theo sản phẩm\n"
            "4. Xem khuyến mãi theo danh mục"
        )

    async def _handle_update_promotion(self, request: ShopAgentRequest) -> ShopAgentResponse:
        return self._create_response(
            "Để cập nhật khuyến mãi, vui lòng cung cấp:\n"
            "1. Mã khuyến mãi cần cập nhật\n"
            "2. Các thông tin cần thay đổi:\n"
            "   - Tên chương trình\n"
            "   - Giá trị khuyến mãi\n"
            "   - Thời gian\n"
            "   - Trạng thái hoạt động\n"
            "   - Các điều kiện khác"
        )

    async def _handle_delete_promotion(self, request: ShopAgentRequest) -> ShopAgentResponse:
        return self._create_response(
            "Để xóa khuyến mãi, vui lòng cung cấp:\n"
            "1. Mã khuyến mãi cần xóa\n"
            "2. Xác nhận xóa"
        )

# Add router endpoints
@router.get("/")
async def get_marketing_campaigns():
    """Get shop marketing campaigns"""
    return {"message": "Get marketing campaigns endpoint"} 