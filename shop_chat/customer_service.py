from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopChatRequest, ShopChatResponse, BaseShopAgent
from repositories.customer_service import CustomerServiceRepository
from datetime import datetime
import json
from typing import Dict, Any
from sqlalchemy.orm import Session

router = APIRouter(prefix="/shop/customer-service", tags=["Shop Customer Service"])

class CustomerServiceAgent(BaseShopAgent):
    def __init__(self, shop_id: int, db: Session):
        super().__init__(shop_id)
        self.customer_service_repository = CustomerServiceRepository(db)

    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "inquiry":
                result = await self._handle_inquiry(action["data"], self.shop_id)
            elif action["type"] == "support":
                result = await self._handle_support(action["data"], self.shop_id)
            elif action["type"] == "feedback":
                result = await self._handle_feedback(action["data"], self.shop_id)
            elif action["type"] == "product_advice":
                result = await self._provide_product_advice(action["data"], self.shop_id)
            else:
                result = {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
            
            return self._create_response(result.get("message", str(result)))
                
        except Exception as e:
            logger.error(f"Error in CustomerServiceAgent: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                error=str(e)
            )

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

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.agent = CustomerServiceAgent(shop_id=1, db=db)  # Pass db to CustomerServiceAgent
        self.customer_service_repository = CustomerServiceRepository(db)

    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        try:
            customer = await self.customer_service_repository.create_customer(customer_data)
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get customer details"""
        try:
            customer = await self.customer_service_repository.get_customer(customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            return customer
        except Exception as e:
            logger.error(f"Error getting customer: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information"""
        try:
            updated_customer = await self.customer_service_repository.update_customer(customer_id, customer_data)
            return updated_customer
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        """Delete a customer"""
        try:
            await self.customer_service_repository.delete_customer(customer_id)
            return {"message": "Customer deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting customer: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_total_customers(self) -> int:
        """Get total number of customers"""
        try:
            return await self.customer_service_repository.get_total_customers()
        except Exception as e:
            logger.error(f"Error getting total customers: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a customer service request"""
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
async def get_customer_service_data():
    """Get customer service data"""
    return {"message": "Get customer service data endpoint"} 