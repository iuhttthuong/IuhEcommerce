from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopChatRequest, ShopChatResponse, BaseShopAgent
from repositories.promotions import PromotionRepository
from models.promotions import PromotionCreate, PromotionUpdate, PromotionType
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

router = APIRouter(prefix="/shop/marketing", tags=["Shop Marketing"])

class MarketingAgent(BaseShopAgent):
    def __init__(self, shop_id: int, db: Session):
        super().__init__(shop_id)
        self.promotion_repository = PromotionRepository(db)

    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
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

    async def _handle_create_promotion(self, request: ShopChatRequest) -> ShopChatResponse:
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

    async def _handle_list_promotions(self, request: ShopChatRequest) -> ShopChatResponse:
        return self._create_response(
            "Để xem danh sách khuyến mãi, vui lòng chọn:\n"
            "1. Xem tất cả khuyến mãi\n"
            "2. Xem khuyến mãi đang hoạt động\n"
            "3. Xem khuyến mãi theo sản phẩm\n"
            "4. Xem khuyến mãi theo danh mục"
        )

    async def _handle_update_promotion(self, request: ShopChatRequest) -> ShopChatResponse:
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

    async def _handle_delete_promotion(self, request: ShopChatRequest) -> ShopChatResponse:
        return self._create_response(
            "Để xóa khuyến mãi, vui lòng cung cấp:\n"
            "1. Mã khuyến mãi cần xóa\n"
            "2. Xác nhận xóa"
        )

class Marketing:
    def __init__(self, db: Session):
        self.db = db
        self.agent = MarketingAgent(shop_id=1, db=db)  # Pass db to MarketingAgent
        self.promotion_repository = PromotionRepository(db)

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new marketing campaign"""
        try:
            promotion = await self.promotion_repository.create(campaign_data)
            return promotion
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Get campaign details"""
        try:
            campaign = await self.promotion_repository.get_by_id(campaign_id)
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            return campaign
        except Exception as e:
            logger.error(f"Error getting campaign: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_campaign(self, campaign_id: int, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign details"""
        try:
            updated_campaign = await self.promotion_repository.update(campaign_id, campaign_data)
            return updated_campaign
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Delete a campaign"""
        try:
            await self.promotion_repository.delete(campaign_id)
            return {"message": "Campaign deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting campaign: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a marketing management request"""
        try:
            response = await self.agent.process_request(ShopChatRequest(**request))
            return response.dict()
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

# Add router endpoints
@router.get("/")
async def get_marketing_campaigns():
    """Get shop marketing campaigns"""
    return {"message": "Get marketing campaigns endpoint"} 