from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.finance import FinanceRepository
from datetime import datetime, timedelta

router = APIRouter(prefix="/shop/finance", tags=["Shop Finance"])

class FinanceAgent:
    def __init__(self):
        self.agent = AssistantAgent(
            name="finance_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về quản lý tài chính cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Theo dõi doanh thu và chi phí
            2. Quản lý thanh toán và hoa hồng
            3. Tạo báo cáo tài chính
            4. Phân tích lợi nhuận
            5. Dự báo tài chính
            
            Bạn cần đảm bảo:
            - Tính toán chính xác các khoản thu chi
            - Báo cáo tài chính minh bạch
            - Phân tích chi tiết và dễ hiểu
            - Đề xuất cải thiện tài chính
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )
        self.finance_repository = FinanceRepository()

    async def process_request(self, request: ShopRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "revenue":
                return await self._analyze_revenue(action["data"], request.shop_id)
            elif action["type"] == "commission":
                return await self._analyze_commission(action["data"], request.shop_id)
            elif action["type"] == "payout":
                return await self._get_payout_info(request.shop_id)
            elif action["type"] == "report":
                return await self._generate_financial_report(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in FinanceAgent: {str(e)}")
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

    async def _analyze_revenue(self, data, shop_id):
        try:
            # Get date range
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            if not start_date or not end_date:
                # Default to last 30 days if not specified
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            
            # Get revenue data
            revenue_data = await self.finance_repository.get_revenue_analysis(
                shop_id=shop_id,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "revenue": {
                    "total_revenue": revenue_data.total_revenue,
                    "net_revenue": revenue_data.net_revenue,
                    "platform_fees": revenue_data.platform_fees,
                    "shipping_fees": revenue_data.shipping_fees,
                    "refunds": revenue_data.refunds,
                    "daily_revenue": revenue_data.daily_revenue
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing revenue: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _analyze_commission(self, data, shop_id):
        try:
            # Get date range
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            if not start_date or not end_date:
                # Default to last 30 days if not specified
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            
            # Get commission data
            commission_data = await self.finance_repository.get_commission_analysis(
                shop_id=shop_id,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "commission": {
                    "total_commission": commission_data.total_commission,
                    "commission_rate": commission_data.commission_rate,
                    "commission_by_category": commission_data.by_category,
                    "commission_trend": commission_data.trend
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing commission: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_payout_info(self, shop_id):
        try:
            # Get payout information
            payout_info = await self.finance_repository.get_payout_info(shop_id)
            
            return {
                "payout": {
                    "available_balance": payout_info.available_balance,
                    "pending_balance": payout_info.pending_balance,
                    "next_payout_date": payout_info.next_payout_date,
                    "payout_method": payout_info.payout_method,
                    "payout_history": payout_info.history
                }
            }
        except Exception as e:
            logger.error(f"Error getting payout info: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _generate_financial_report(self, data, shop_id):
        try:
            # Validate report parameters
            report_type = data.get("report_type")
            if not report_type:
                raise HTTPException(status_code=400, detail="Report type is required")
            
            # Generate financial report
            report = await self.finance_repository.generate_financial_report(
                shop_id=shop_id,
                report_type=report_type,
                start_date=data.get("start_date"),
                end_date=data.get("end_date")
            )
            
            return {
                "report_type": report_type,
                "generated_at": datetime.now(),
                "period": {
                    "start_date": report.start_date,
                    "end_date": report.end_date
                },
                "summary": {
                    "total_revenue": report.total_revenue,
                    "total_expenses": report.total_expenses,
                    "net_profit": report.net_profit,
                    "profit_margin": report.profit_margin
                },
                "details": report.details,
                "recommendations": report.recommendations
            }
        except Exception as e:
            logger.error(f"Error generating financial report: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.get("/")
async def get_financial_data():
    """Get shop financial data"""
    return {"message": "Get financial data endpoint"} 