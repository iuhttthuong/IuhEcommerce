from fastapi import HTTPException, APIRouter, Depends
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from pydantic import BaseModel
from typing import Optional, Dict, Any
from db import Session, get_db
from models.shops import Shop
from repositories.policies import PolicyRepository
from datetime import datetime

router = APIRouter(prefix="/shop/policy", tags=["Shop Policy"])

class PolicyRequest(BaseModel):
    shop_id: int
    policy_type: str  # e.g., "return", "shipping", "payment", "warranty"
    context: Optional[Dict[str, Any]] = None

class PolicyResponse(BaseModel):
    policy_info: Dict[str, Any]
    explanation: str

class PolicyAgent:
    def __init__(self):
        self.agent = AssistantAgent(
            name="policy_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về quản lý chính sách và tuân thủ cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Quản lý chính sách shop
            2. Đảm bảo tuân thủ quy định
            3. Xử lý khiếu nại và tranh chấp
            4. Tư vấn chính sách bảo hành
            5. Hướng dẫn quy trình giải quyết vấn đề
            
            Bạn cần đảm bảo:
            - Tuân thủ đúng quy định của sàn
            - Xử lý công bằng và minh bạch
            - Bảo vệ quyền lợi của cả shop và người mua
            - Cập nhật kịp thời các thay đổi chính sách
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )
        self.policy_repository = PolicyRepository()

    async def process_request(self, request: ShopRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "policy":
                return await self._get_shop_policy(request.shop_id)
            elif action["type"] == "compliance":
                return await self._check_compliance(action["data"], request.shop_id)
            elif action["type"] == "dispute":
                return await self._handle_dispute(action["data"], request.shop_id)
            elif action["type"] == "warranty":
                return await self._get_warranty_info(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in PolicyAgent: {str(e)}")
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

    async def _get_shop_policy(self, shop_id):
        try:
            # Get shop policies
            policies = await self.policy_repository.get_shop_policies(shop_id)
            
            return {
                "policies": {
                    "return_policy": policies.return_policy,
                    "shipping_policy": policies.shipping_policy,
                    "warranty_policy": policies.warranty_policy,
                    "payment_policy": policies.payment_policy,
                    "last_updated": policies.last_updated
                }
            }
        except Exception as e:
            logger.error(f"Error getting shop policies: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _check_compliance(self, data, shop_id):
        try:
            # Check compliance with platform policies
            compliance_report = await self.policy_repository.check_compliance(
                shop_id=shop_id,
                policy_type=data.get("policy_type"),
                check_items=data.get("check_items", [])
            )
            
            return {
                "compliance_report": {
                    "status": compliance_report.status,
                    "violations": compliance_report.violations,
                    "warnings": compliance_report.warnings,
                    "recommendations": compliance_report.recommendations,
                    "checked_at": datetime.now()
                }
            }
        except Exception as e:
            logger.error(f"Error checking compliance: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _handle_dispute(self, data, shop_id):
        try:
            # Handle customer dispute
            dispute_result = await self.policy_repository.handle_dispute(
                shop_id=shop_id,
                dispute_id=data.get("dispute_id"),
                action=data.get("action"),
                resolution=data.get("resolution")
            )
            
            return {
                "dispute": {
                    "dispute_id": dispute_result.dispute_id,
                    "status": dispute_result.status,
                    "resolution": dispute_result.resolution,
                    "resolved_at": dispute_result.resolved_at,
                    "notes": dispute_result.notes
                }
            }
        except Exception as e:
            logger.error(f"Error handling dispute: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_warranty_info(self, data, shop_id):
        try:
            # Get warranty information
            warranty_info = await self.policy_repository.get_warranty_info(
                shop_id=shop_id,
                product_id=data.get("product_id")
            )
            
            return {
                "warranty": {
                    "product_id": warranty_info.product_id,
                    "warranty_period": warranty_info.warranty_period,
                    "warranty_terms": warranty_info.warranty_terms,
                    "coverage": warranty_info.coverage,
                    "exclusions": warranty_info.exclusions,
                    "claim_process": warranty_info.claim_process
                }
            }
        except Exception as e:
            logger.error(f"Error getting warranty info: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.post("/query", response_model=PolicyResponse)
async def query_policy(request: PolicyRequest, db: Session = Depends(get_db)):
    try:
        # Get shop information
        shop = db.query(Shop).filter(Shop.seller_id == request.shop_id).first()
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        
        # Prepare context
        context = request.context or {}
        context.update({
            "shop_info": {
                "seller_id": shop.seller_id,
                "name": shop.name
            },
            "policy_type": request.policy_type
        })
        
        # Create the message for the assistant
        message = {
            "role": "user",
            "content": f"""
            Context: {context}
            Please provide information about the {request.policy_type} policy for this shop.
            """
        }
        
        # Get response from the assistant
        response = await PolicyAssistant.a_generate_reply(messages=[message])
        
        # Parse the response to extract policy information and explanation
        policy_info = {
            "shop_id": shop.seller_id,
            "shop_name": shop.name,
            "policy_type": request.policy_type
        }
        
        return PolicyResponse(
            policy_info=policy_info,
            explanation=response
        )
        
    except Exception as e:
        logger.error(f"Error in policy query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 