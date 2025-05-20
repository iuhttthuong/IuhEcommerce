from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.analytics import AnalyticsRepository
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
from .base import BaseShopAgent, ShopAgentRequest, ShopAgentResponse

router = APIRouter(prefix="/shop/analytics", tags=["Shop Analytics"])

class AnalyticsAgent(BaseShopAgent):
    def __init__(self, shop_id: int):
        super().__init__(shop_id, "analytics")
        self.analytics_repository = AnalyticsRepository()

    async def process(self, request: ShopAgentRequest) -> ShopAgentResponse:
        message = request.message.lower()
        
        if "doanh số" in message or "doanh thu" in message:
            return await self._handle_sales_analytics(request)
        elif "sản phẩm" in message:
            return await self._handle_product_analytics(request)
        elif "khách hàng" in message:
            return await self._handle_customer_analytics(request)
        elif "marketing" in message or "khuyến mãi" in message:
            return await self._handle_marketing_analytics(request)
        elif "tổng quan" in message or "tổng hợp" in message:
            return await self._handle_overview_analytics(request)
        else:
            return self._create_response(
                "Tôi có thể giúp bạn phân tích dữ liệu. "
                "Bạn có thể:\n"
                "- Xem phân tích doanh số\n"
                "- Xem phân tích sản phẩm\n"
                "- Xem phân tích khách hàng\n"
                "- Xem phân tích marketing\n"
                "- Xem báo cáo tổng quan\n"
                "Bạn muốn xem phân tích nào?"
            )

    async def _handle_sales_analytics(self, request: ShopAgentRequest) -> ShopAgentResponse:
        # Default to last 30 days if no date range specified
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            self.db,
            self.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "sales" not in summary:
            return self._create_response(
                "Không có dữ liệu doanh số trong khoảng thời gian này."
            )
        
        sales = summary["sales"]
        response = "Phân tích doanh số:\n"
        response += f"Tổng doanh thu: {sales['total_sales']:,.0f} VNĐ\n"
        response += f"Tổng số đơn hàng: {sales['total_orders']}\n"
        response += f"Giá trị đơn hàng trung bình: {sales['average_order_value']:,.0f} VNĐ\n"
        response += f"Tỷ lệ chuyển đổi: {sales['conversion_rate']:.1%}\n"
        response += f"Tỷ lệ hoàn trả: {sales['refund_rate']:.1%}"
        
        return self._create_response(response)

    async def _handle_product_analytics(self, request: ShopAgentRequest) -> ShopAgentResponse:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            self.db,
            self.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "products" not in summary:
            return self._create_response(
                "Không có dữ liệu sản phẩm trong khoảng thời gian này."
            )
        
        products = summary["products"]
        response = "Phân tích sản phẩm:\n"
        response += f"Tổng số sản phẩm: {products['total_products']}\n"
        response += f"Sản phẩm đang bán: {products['active_products']}\n"
        
        if products['top_selling_products']:
            response += "\nSản phẩm bán chạy:\n"
            for product_id, quantity in list(products['top_selling_products'].items())[:5]:
                response += f"- Sản phẩm {product_id}: {quantity} đơn vị\n"
        
        if products['low_stock_products']:
            response += "\nSản phẩm sắp hết hàng:\n"
            for product_id, stock in list(products['low_stock_products'].items())[:5]:
                response += f"- Sản phẩm {product_id}: còn {stock} đơn vị\n"
        
        return self._create_response(response)

    async def _handle_customer_analytics(self, request: ShopAgentRequest) -> ShopAgentResponse:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            self.db,
            self.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "customers" not in summary:
            return self._create_response(
                "Không có dữ liệu khách hàng trong khoảng thời gian này."
            )
        
        customers = summary["customers"]
        response = "Phân tích khách hàng:\n"
        response += f"Tổng số khách hàng: {customers['total_customers']}\n"
        response += f"Khách hàng mới: {customers['new_customers']}\n"
        response += f"Khách hàng quay lại: {customers['returning_customers']}\n"
        response += f"Đánh giá trung bình: {customers['customer_satisfaction']:.1f}/5.0"
        
        return self._create_response(response)

    async def _handle_marketing_analytics(self, request: ShopAgentRequest) -> ShopAgentResponse:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            self.db,
            self.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "marketing" not in summary:
            return self._create_response(
                "Không có dữ liệu marketing trong khoảng thời gian này."
            )
        
        marketing = summary["marketing"]
        response = "Phân tích marketing:\n"
        response += f"Tổng số khuyến mãi: {marketing['total_promotions']}\n"
        response += f"Khuyến mãi đang chạy: {marketing['active_promotions']}\n"
        response += f"Chi phí marketing: {marketing['marketing_costs']:,.0f} VNĐ\n"
        response += f"ROI marketing: {marketing['marketing_roi']:.1%}"
        
        if marketing['promotion_effectiveness']:
            response += "\n\nHiệu quả khuyến mãi:\n"
            for promo_id, rate in list(marketing['promotion_effectiveness'].items())[:5]:
                response += f"- Khuyến mãi {promo_id}: {rate:.1%}\n"
        
        return self._create_response(response)

    async def _handle_overview_analytics(self, request: ShopAgentRequest) -> ShopAgentResponse:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            self.db,
            self.shop_id,
            start_date,
            end_date
        )
        
        if not summary:
            return self._create_response(
                "Không có dữ liệu tổng quan trong khoảng thời gian này."
            )
        
        response = "Báo cáo tổng quan:\n\n"
        
        if "sales" in summary:
            sales = summary["sales"]
            response += "Doanh số:\n"
            response += f"- Tổng doanh thu: {sales['total_sales']:,.0f} VNĐ\n"
            response += f"- Tổng đơn hàng: {sales['total_orders']}\n"
            response += f"- Giá trị đơn trung bình: {sales['average_order_value']:,.0f} VNĐ\n\n"
        
        if "products" in summary:
            products = summary["products"]
            response += "Sản phẩm:\n"
            response += f"- Tổng số sản phẩm: {products['total_products']}\n"
            response += f"- Sản phẩm đang bán: {products['active_products']}\n\n"
        
        if "customers" in summary:
            customers = summary["customers"]
            response += "Khách hàng:\n"
            response += f"- Tổng số khách hàng: {customers['total_customers']}\n"
            response += f"- Khách hàng mới: {customers['new_customers']}\n"
            response += f"- Khách hàng quay lại: {customers['returning_customers']}\n\n"
        
        if "marketing" in summary:
            marketing = summary["marketing"]
            response += "Marketing:\n"
            response += f"- Khuyến mãi đang chạy: {marketing['active_promotions']}\n"
            response += f"- ROI marketing: {marketing['marketing_roi']:.1%}"
        
        return self._create_response(response)

# Add router endpoints
@router.get("/")
async def get_shop_analytics():
    """Get shop analytics data"""
    return {"message": "Get analytics endpoint"} 