from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.promotions import PromotionRepository
from models.promotions import PromotionCreate, PromotionUpdate

router = APIRouter(prefix="/shop/marketing", tags=["Shop Marketing"])

class MarketingAgent:
    def __init__(self):
        self.agent = AssistantAgent(
            name="marketing_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về marketing và khuyến mãi cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Tạo và quản lý chương trình khuyến mãi
            2. Tạo mã giảm giá
            3. Phân tích hiệu quả chiến dịch
            4. Đề xuất chiến lược marketing
            5. Quản lý quảng cáo
            
            Bạn cần đảm bảo:
            - Tạo khuyến mãi hấp dẫn và hiệu quả
            - Tuân thủ quy định về khuyến mãi của sàn
            - Phân tích và báo cáo kết quả
            - Đề xuất chiến lược phù hợp
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )
        self.promotion_repository = PromotionRepository()

    async def process_request(self, request: ShopRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "create":
                return await self._create_promotion(action["data"], request.shop_id)
            elif action["type"] == "update":
                return await self._update_promotion(action["data"], request.shop_id)
            elif action["type"] == "list":
                return await self._list_promotions(request.shop_id)
            elif action["type"] == "analyze":
                return await self._analyze_campaign(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in MarketingAgent: {str(e)}")
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

    async def _create_promotion(self, data, shop_id):
        try:
            # Validate required fields
            required_fields = ["name", "type", "start_date", "end_date"]
            for field in required_fields:
                if field not in data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            # Create promotion
            promotion_data = PromotionCreate(
                shop_id=shop_id,
                name=data["name"],
                type=data["type"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                discount_value=data.get("discount_value"),
                min_order_value=data.get("min_order_value"),
                max_discount=data.get("max_discount"),
                conditions=data.get("conditions", {}),
                description=data.get("description")
            )
            
            promotion = await self.promotion_repository.create(promotion_data)
            return {
                "message": "Chương trình khuyến mãi đã được tạo thành công",
                "promotion": promotion
            }
        except Exception as e:
            logger.error(f"Error creating promotion: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _update_promotion(self, data, shop_id):
        try:
            promotion_id = data.get("promotion_id")
            if not promotion_id:
                raise HTTPException(status_code=400, detail="Promotion ID is required")
            
            # Verify promotion belongs to shop
            promotion = await self.promotion_repository.get_by_id(promotion_id)
            if not promotion or promotion.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Promotion not found")
            
            # Update promotion
            update_data = PromotionUpdate(**data)
            updated_promotion = await self.promotion_repository.update(promotion_id, update_data)
            
            return {
                "message": "Chương trình khuyến mãi đã được cập nhật thành công",
                "promotion": updated_promotion
            }
        except Exception as e:
            logger.error(f"Error updating promotion: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _list_promotions(self, shop_id):
        try:
            # Get all active promotions for shop
            promotions = await self.promotion_repository.get_active_by_shop_id(shop_id)
            
            return {
                "promotions": promotions,
                "total": len(promotions)
            }
        except Exception as e:
            logger.error(f"Error listing promotions: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _analyze_campaign(self, data, shop_id):
        try:
            promotion_id = data.get("promotion_id")
            if not promotion_id:
                raise HTTPException(status_code=400, detail="Promotion ID is required")
            
            # Verify promotion belongs to shop
            promotion = await self.promotion_repository.get_by_id(promotion_id)
            if not promotion or promotion.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Promotion not found")
            
            # Get campaign analytics
            analytics = await self.promotion_repository.get_campaign_analytics(promotion_id)
            
            return {
                "promotion_id": promotion_id,
                "name": promotion.name,
                "analytics": {
                    "total_orders": analytics.total_orders,
                    "total_revenue": analytics.total_revenue,
                    "total_discount": analytics.total_discount,
                    "conversion_rate": analytics.conversion_rate,
                    "average_order_value": analytics.average_order_value
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing campaign: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.get("/")
async def get_marketing_campaigns():
    """Get shop marketing campaigns"""
    return {"message": "Get marketing campaigns endpoint"} 