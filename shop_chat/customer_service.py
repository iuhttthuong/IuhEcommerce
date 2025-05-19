from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.customer_service import CustomerServiceRepository
from datetime import datetime

router = APIRouter(prefix="/shop/customer-service", tags=["Shop Customer Service"])

class CustomerServiceAgent:
    def __init__(self):
        self.agent = AssistantAgent(
            name="customer_service_agent",
            system_message="""Bạn là một trợ lý AI chuyên về dịch vụ khách hàng cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Trả lời câu hỏi của khách hàng
            2. Hỗ trợ giải quyết vấn đề
            3. Xử lý phản hồi và đánh giá
            4. Tư vấn sản phẩm
            5. Hỗ trợ đơn hàng
            
            Bạn cần đảm bảo:
            - Phản hồi nhanh chóng và chính xác
            - Thái độ thân thiện và chuyên nghiệp
            - Giải quyết triệt để vấn đề
            - Duy trì chất lượng dịch vụ
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )
        self.customer_service_repository = CustomerServiceRepository()

    async def process_request(self, request: ShopRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "inquiry":
                return await self._handle_inquiry(action["data"], request.shop_id)
            elif action["type"] == "support":
                return await self._handle_support(action["data"], request.shop_id)
            elif action["type"] == "feedback":
                return await self._handle_feedback(action["data"], request.shop_id)
            elif action["type"] == "product_advice":
                return await self._provide_product_advice(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in CustomerServiceAgent: {str(e)}")
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

    async def _handle_inquiry(self, data, shop_id):
        try:
            # Handle customer inquiry
            inquiry_result = await self.customer_service_repository.handle_inquiry(
                shop_id=shop_id,
                inquiry_type=data.get("inquiry_type"),
                message=data.get("message"),
                customer_id=data.get("customer_id")
            )
            
            return {
                "inquiry": {
                    "inquiry_id": inquiry_result.inquiry_id,
                    "status": inquiry_result.status,
                    "response": inquiry_result.response,
                    "handled_at": inquiry_result.handled_at,
                    "follow_up_required": inquiry_result.follow_up_required
                }
            }
        except Exception as e:
            logger.error(f"Error handling inquiry: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _handle_support(self, data, shop_id):
        try:
            # Handle customer support request
            support_result = await self.customer_service_repository.handle_support(
                shop_id=shop_id,
                support_type=data.get("support_type"),
                issue=data.get("issue"),
                customer_id=data.get("customer_id"),
                order_id=data.get("order_id")
            )
            
            return {
                "support": {
                    "support_id": support_result.support_id,
                    "status": support_result.status,
                    "resolution": support_result.resolution,
                    "resolved_at": support_result.resolved_at,
                    "satisfaction_rating": support_result.satisfaction_rating
                }
            }
        except Exception as e:
            logger.error(f"Error handling support: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _handle_feedback(self, data, shop_id):
        try:
            # Handle customer feedback
            feedback_result = await self.customer_service_repository.handle_feedback(
                shop_id=shop_id,
                feedback_type=data.get("feedback_type"),
                rating=data.get("rating"),
                comment=data.get("comment"),
                customer_id=data.get("customer_id"),
                order_id=data.get("order_id")
            )
            
            return {
                "feedback": {
                    "feedback_id": feedback_result.feedback_id,
                    "status": feedback_result.status,
                    "response": feedback_result.response,
                    "handled_at": feedback_result.handled_at,
                    "improvement_actions": feedback_result.improvement_actions
                }
            }
        except Exception as e:
            logger.error(f"Error handling feedback: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _provide_product_advice(self, data, shop_id):
        try:
            # Provide product advice to customer
            advice_result = await self.customer_service_repository.provide_product_advice(
                shop_id=shop_id,
                customer_id=data.get("customer_id"),
                preferences=data.get("preferences"),
                budget=data.get("budget"),
                category=data.get("category")
            )
            
            return {
                "product_advice": {
                    "recommendations": advice_result.recommendations,
                    "reasoning": advice_result.reasoning,
                    "alternatives": advice_result.alternatives,
                    "provided_at": datetime.now()
                }
            }
        except Exception as e:
            logger.error(f"Error providing product advice: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.get("/")
async def get_customer_service_data():
    """Get customer service data"""
    return {"message": "Get customer service data endpoint"} 