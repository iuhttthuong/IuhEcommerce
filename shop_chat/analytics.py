from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.analytics import AnalyticsRepository
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/shop/analytics", tags=["Shop Analytics"])

class AnalyticsAgent:
    def __init__(self):
        self.agent = AssistantAgent(
            name="analytics_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về phân tích dữ liệu và báo cáo cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Phân tích doanh số bán hàng
            2. Theo dõi hiệu suất sản phẩm
            3. Phân tích hành vi khách hàng
            4. Tạo báo cáo tùy chỉnh
            5. Đề xuất cải thiện
            
            Bạn cần đảm bảo:
            - Phân tích dữ liệu chính xác và chi tiết
            - Trình bày báo cáo dễ hiểu
            - Đề xuất hành động dựa trên dữ liệu
            - Cập nhật báo cáo theo thời gian thực
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )
        self.analytics_repository = AnalyticsRepository()

    async def process_request(self, request: ShopRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "sales":
                return await self._analyze_sales(action["data"], request.shop_id)
            elif action["type"] == "products":
                return await self._analyze_products(action["data"], request.shop_id)
            elif action["type"] == "customers":
                return await self._analyze_customers(action["data"], request.shop_id)
            elif action["type"] == "custom":
                return await self._generate_custom_report(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in AnalyticsAgent: {str(e)}")
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

    async def _analyze_sales(self, data, shop_id):
        try:
            # Get date range
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            if not start_date or not end_date:
                # Default to last 30 days if not specified
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            
            # Get sales analytics
            sales_data = await self.analytics_repository.get_sales_analytics(
                shop_id=shop_id,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "sales": {
                    "total_revenue": sales_data.total_revenue,
                    "total_orders": sales_data.total_orders,
                    "average_order_value": sales_data.average_order_value,
                    "daily_sales": sales_data.daily_sales,
                    "top_selling_categories": sales_data.top_categories,
                    "payment_methods": sales_data.payment_methods
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing sales: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _analyze_products(self, data, shop_id):
        try:
            # Get product analytics
            product_data = await self.analytics_repository.get_product_analytics(
                shop_id=shop_id,
                product_id=data.get("product_id")
            )
            
            return {
                "products": {
                    "total_products": product_data.total_products,
                    "active_products": product_data.active_products,
                    "top_selling_products": product_data.top_selling,
                    "low_stock_products": product_data.low_stock,
                    "product_performance": product_data.performance
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing products: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _analyze_customers(self, data, shop_id):
        try:
            # Get customer analytics
            customer_data = await self.analytics_repository.get_customer_analytics(
                shop_id=shop_id,
                start_date=data.get("start_date"),
                end_date=data.get("end_date")
            )
            
            return {
                "customers": {
                    "total_customers": customer_data.total_customers,
                    "new_customers": customer_data.new_customers,
                    "returning_customers": customer_data.returning_customers,
                    "customer_segments": customer_data.segments,
                    "purchase_frequency": customer_data.purchase_frequency,
                    "customer_lifetime_value": customer_data.lifetime_value
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing customers: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _generate_custom_report(self, data, shop_id):
        try:
            # Validate report parameters
            report_type = data.get("report_type")
            if not report_type:
                raise HTTPException(status_code=400, detail="Report type is required")
            
            # Generate custom report
            report = await self.analytics_repository.generate_custom_report(
                shop_id=shop_id,
                report_type=report_type,
                parameters=data.get("parameters", {}),
                start_date=data.get("start_date"),
                end_date=data.get("end_date")
            )
            
            return {
                "report_type": report_type,
                "generated_at": datetime.now(),
                "data": report.data,
                "summary": report.summary,
                "recommendations": report.recommendations
            }
        except Exception as e:
            logger.error(f"Error generating custom report: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.get("/")
async def get_shop_analytics():
    """Get shop analytics data"""
    return {"message": "Get analytics endpoint"} 