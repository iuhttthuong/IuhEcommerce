from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.analytics import AnalyticsRepository
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

router = APIRouter(prefix="/shop/analytics", tags=["Shop Analytics"])

class AnalyticsAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="AnalyticsAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên phân tích và báo cáo dữ liệu cho người bán.

Nhiệm vụ của bạn:
1. Phân tích doanh số và doanh thu
2. Phân tích sản phẩm và tồn kho
3. Phân tích khách hàng và tương tác
4. Phân tích marketing và khuyến mãi
5. Tổng hợp báo cáo tổng quan

Khi trả lời, bạn cần:
- Cung cấp dữ liệu chính xác và đầy đủ
- Phân tích xu hướng và mẫu hình
- Đề xuất cải thiện và tối ưu
- Sử dụng ngôn ngữ chuyên nghiệp
- Trình bày dữ liệu dễ hiểu"""
        )
        self.analytics_repository = AnalyticsRepository(Session())
        self.collection_name = "analytics_embeddings"
        self.agent_name = "AnalyticsAgent"

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Người bán hỏi: {query}\n"
            f"Thông tin phân tích liên quan:\n{context}\n"
            "Hãy trả lời theo cấu trúc sau:\n"
            "1. Tóm tắt dữ liệu:\n"
            "   - Thời gian phân tích\n"
            "   - Phạm vi dữ liệu\n"
            "   - Các chỉ số chính\n\n"
            "2. Phân tích chi tiết:\n"
            "   - Xu hướng và mẫu hình\n"
            "   - So sánh với kỳ trước\n"
            "   - Điểm mạnh và điểm yếu\n\n"
            "3. Đề xuất cải thiện:\n"
            "   - Các cơ hội tăng trưởng\n"
            "   - Giải pháp tối ưu\n"
            "   - Kế hoạch hành động\n\n"
            "Trả lời cần:\n"
            "- Chính xác và đầy đủ\n"
            "- Dễ hiểu và trực quan\n"
            "- Có tính thực tế cao\n"
            "- Đề xuất cụ thể"
        )

    def _get_response_title(self, query: str) -> str:
        return f"Phân tích {query.split()[0] if query else 'tổng quan'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy dữ liệu phân tích cho yêu cầu này. Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ shop."

    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        # Placeholder implementation. Replace with actual logic as needed.
        return {
            "response": {
                "title": self._get_response_title(request.message),
                "content": "Analytics processing not yet implemented.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.name,
            "context": {
                "search_results": [],
                "shop_id": request.shop_id
            },
            "timestamp": datetime.now().isoformat()
        }

    async def process_request(self, request: ShopRequest) -> Dict[str, Any]:
        try:
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
                return {
                    "response": {
                        "title": "Phân tích dữ liệu",
                        "content": "Tôi có thể giúp bạn phân tích dữ liệu. Bạn có thể:\n- Xem phân tích doanh số\n- Xem phân tích sản phẩm\n- Xem phân tích khách hàng\n- Xem phân tích marketing\n- Xem báo cáo tổng quan\nBạn muốn xem phân tích nào?",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "agent": self.agent_name,
                    "context": {},
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error in process_request: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "response": {
                    "title": "Lỗi xử lý yêu cầu",
                    "content": "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }

    async def _handle_sales_analytics(self, request: ShopRequest) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            request.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "sales" not in summary:
            return {
                "response": {
                    "title": "Phân tích doanh số",
                    "content": "Không có dữ liệu doanh số trong khoảng thời gian này.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }
        
        sales = summary["sales"]
        response_content = "Phân tích doanh số:\n"
        response_content += f"Tổng doanh thu: {sales['total_sales']:,.0f} VNĐ\n"
        response_content += f"Tổng số đơn hàng: {sales['total_orders']}\n"
        response_content += f"Giá trị đơn hàng trung bình: {sales['average_order_value']:,.0f} VNĐ\n"
        response_content += f"Tỷ lệ chuyển đổi: {sales['conversion_rate']:.1%}\n"
        response_content += f"Tỷ lệ hoàn trả: {sales['refund_rate']:.1%}"
        
        return {
            "response": {
                "title": "Phân tích doanh số",
                "content": response_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.agent_name,
            "context": {"summary": summary},
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_product_analytics(self, request: ShopRequest) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            request.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "products" not in summary:
            return {
                "response": {
                    "title": "Phân tích sản phẩm",
                    "content": "Không có dữ liệu sản phẩm trong khoảng thời gian này.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }
        
        products = summary["products"]
        response_content = "Phân tích sản phẩm:\n"
        response_content += f"Tổng số sản phẩm: {products['total_products']}\n"
        response_content += f"Sản phẩm đang bán: {products['active_products']}\n"
        
        if products['top_selling_products']:
            response_content += "\nSản phẩm bán chạy:\n"
            for product_id, quantity in list(products['top_selling_products'].items())[:5]:
                response_content += f"- Sản phẩm {product_id}: {quantity} đơn vị\n"
        
        if products['low_stock_products']:
            response_content += "\nSản phẩm sắp hết hàng:\n"
            for product_id, stock in list(products['low_stock_products'].items())[:5]:
                response_content += f"- Sản phẩm {product_id}: còn {stock} đơn vị\n"
        
        return {
            "response": {
                "title": "Phân tích sản phẩm",
                "content": response_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.agent_name,
            "context": {"summary": summary},
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_customer_analytics(self, request: ShopRequest) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            request.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "customers" not in summary:
            return {
                "response": {
                    "title": "Phân tích khách hàng",
                    "content": "Không có dữ liệu khách hàng trong khoảng thời gian này.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }
        
        customers = summary["customers"]
        response_content = "Phân tích khách hàng:\n"
        response_content += f"Tổng số khách hàng: {customers['total_customers']}\n"
        response_content += f"Khách hàng mới: {customers['new_customers']}\n"
        response_content += f"Khách hàng quay lại: {customers['returning_customers']}\n"
        response_content += f"Đánh giá trung bình: {customers['customer_satisfaction']:.1f}/5.0"
        
        return {
            "response": {
                "title": "Phân tích khách hàng",
                "content": response_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.agent_name,
            "context": {"summary": summary},
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_marketing_analytics(self, request: ShopRequest) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            request.shop_id,
            start_date,
            end_date
        )
        
        if not summary or "marketing" not in summary:
            return {
                "response": {
                    "title": "Phân tích marketing",
                    "content": "Không có dữ liệu marketing trong khoảng thời gian này.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }
        
        marketing = summary["marketing"]
        response_content = "Phân tích marketing:\n"
        response_content += f"Tổng số khuyến mãi: {marketing['total_promotions']}\n"
        response_content += f"Khuyến mãi đang chạy: {marketing['active_promotions']}\n"
        response_content += f"Chi phí marketing: {marketing['marketing_costs']:,.0f} VNĐ\n"
        response_content += f"ROI marketing: {marketing['marketing_roi']:.1%}"
        
        if marketing['promotion_effectiveness']:
            response_content += "\n\nHiệu quả khuyến mãi:\n"
            for promo_id, rate in list(marketing['promotion_effectiveness'].items())[:5]:
                response_content += f"- Khuyến mãi {promo_id}: {rate:.1%}\n"
        
        return {
            "response": {
                "title": "Phân tích marketing",
                "content": response_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.agent_name,
            "context": {"summary": summary},
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_overview_analytics(self, request: ShopRequest) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        summary = self.analytics_repository.get_analytics_summary(
            request.shop_id,
            start_date,
            end_date
        )
        
        if not summary:
            return {
                "response": {
                    "title": "Báo cáo tổng quan",
                    "content": "Không có dữ liệu tổng quan trong khoảng thời gian này.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }
        
        response_content = "Báo cáo tổng quan:\n\n"
        
        if "sales" in summary:
            sales = summary["sales"]
            response_content += "Doanh số:\n"
            response_content += f"- Tổng doanh thu: {sales['total_sales']:,.0f} VNĐ\n"
            response_content += f"- Tổng đơn hàng: {sales['total_orders']}\n"
            response_content += f"- Giá trị đơn trung bình: {sales['average_order_value']:,.0f} VNĐ\n\n"
        
        if "products" in summary:
            products = summary["products"]
            response_content += "Sản phẩm:\n"
            response_content += f"- Tổng số sản phẩm: {products['total_products']}\n"
            response_content += f"- Sản phẩm đang bán: {products['active_products']}\n\n"
        
        if "customers" in summary:
            customers = summary["customers"]
            response_content += "Khách hàng:\n"
            response_content += f"- Tổng số khách hàng: {customers['total_customers']}\n"
            response_content += f"- Khách hàng mới: {customers['new_customers']}\n"
            response_content += f"- Khách hàng quay lại: {customers['returning_customers']}\n\n"
        
        if "marketing" in summary:
            marketing = summary["marketing"]
            response_content += "Marketing:\n"
            response_content += f"- Khuyến mãi đang chạy: {marketing['active_promotions']}\n"
            response_content += f"- ROI marketing: {marketing['marketing_roi']:.1%}"
        
        return {
            "response": {
                "title": "Báo cáo tổng quan",
                "content": response_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.agent_name,
            "context": {"summary": summary},
            "timestamp": datetime.now().isoformat()
        }

class Analytics:
    def __init__(self, db: Session):
        self.db = db
        self.agent = AnalyticsAgent()
        self.analytics_repository = AnalyticsRepository(db)

    async def get_analytics(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get analytics data"""
        try:
            shop_request = ShopRequest(**request)
            response = await self.agent.process_request(shop_request)
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "response": {
                    "title": "Lỗi xử lý yêu cầu",
                    "content": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": "AnalyticsAgent",
                "context": {},
                "timestamp": datetime.now().isoformat()
            }

@router.post("/query")
async def query_analytics(request: ChatMessageRequest):
    try:
        analytics = Analytics(Session())
        shop_request = ShopRequest(
            message=request.content,
            chat_id=request.chat_id,
            shop_id=request.sender_id if request.sender_type == "shop" else None,
            user_id=request.sender_id if request.sender_type == "user" else None,
            context=request.message_metadata if request.message_metadata else {},
            entities={},
            agent_messages=[],
            filters={}
        )
        response = await analytics.get_analytics(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_analytics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_shop_analytics():
    """Get shop analytics"""
    return {"message": "Get shop analytics endpoint"} 