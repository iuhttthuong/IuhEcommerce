from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.analytics import AnalyticsRepository
from repositories.message import MessageRepository
from models.chats import ChatMessageCreate
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from services.search import SearchServices
import traceback

router = APIRouter(prefix="/shop/analytics", tags=["Shop Analytics"])

class AnalyticsAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="AnalyticsAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và hướng dẫn cho người bán về phân tích dữ liệu và báo cáo.

Nhiệm vụ của bạn:
1. Phân tích dữ liệu bán hàng
2. Tạo báo cáo thống kê
3. Đề xuất cải thiện
4. Dự đoán xu hướng

Các chức năng chính:
1. Báo cáo doanh số:
   - Thống kê doanh thu
   - Phân tích sản phẩm
   - Theo dõi hiệu quả
   - Đánh giá tăng trưởng
   - Dự báo xu hướng

2. Thống kê bán hàng:
   - Số lượng đơn hàng
   - Giá trị đơn hàng
   - Tỷ lệ chuyển đổi
   - Phân tích khách hàng
   - Đánh giá hiệu quả

3. Phân tích hiệu quả:
   - Hiệu suất sản phẩm
   - Tỷ lệ lợi nhuận
   - Chi phí vận hành
   - ROI marketing
   - Tối ưu chi phí

4. Báo cáo tồn kho:
   - Mức tồn kho
   - Tỷ lệ quay vòng
   - Dự báo nhu cầu
   - Tối ưu tồn kho
   - Cảnh báo hết hàng

5. Báo cáo khách hàng:
   - Phân tích hành vi
   - Đánh giá trải nghiệm
   - Tỷ lệ quay lại
   - Giá trị khách hàng
   - Phân khúc khách hàng

Khi trả lời, bạn cần:
- Tập trung vào dữ liệu thực tế
- Cung cấp phân tích chi tiết
- Đề xuất giải pháp tối ưu
- Sử dụng ngôn ngữ chuyên nghiệp
- Cung cấp ví dụ cụ thể
- Nhấn mạnh các điểm quan trọng
- Hướng dẫn từng bước khi cần"""
        )
        self.analytics_repository = AnalyticsRepository(Session())
        self.message_repository = MessageRepository()
        self.collection_name = "analytics_embeddings"
        self.agent_name = "AnalyticsAgent"

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytics request."""
        try:
            message = request.get('message', '')
            shop_id = request.get('shop_id')
            chat_history = request.get('chat_history', '')
            
            if not shop_id:
                return {
                    "message": "Không tìm thấy thông tin shop.",
                    "type": "error"
                }

            # Tạo prompt cho LLM
            prompt = self._build_prompt(message, f"Shop ID: {shop_id}\nChat History:\n{chat_history}")
            
            # Tạo response sử dụng assistant
            response = await self.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "message": response if response else self._get_fallback_response(),
                "type": "text"
            }
            
        except Exception as e:
            logger.error(f"Error in AnalyticsAgent.process: {str(e)}")
            return {
                "message": self._get_fallback_response(),
                "type": "error"
            }

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Người bán hỏi: {query}\n"
            f"Thông tin phân tích dữ liệu liên quan:\n{context}\n"
            "Hãy trả lời theo cấu trúc sau:\n"
            "1. Tóm tắt yêu cầu:\n"
            "   - Mục đích phân tích\n"
            "   - Phạm vi dữ liệu\n"
            "   - Thời gian phân tích\n\n"
            "2. Phân tích chi tiết:\n"
            "   - Các chỉ số quan trọng\n"
            "   - Xu hướng và mẫu hình\n"
            "   - So sánh và đánh giá\n\n"
            "3. Kết quả và hiểu biết:\n"
            "   - Kết quả chính\n"
            "   - Hiểu biết sâu sắc\n"
            "   - Điểm cần lưu ý\n\n"
            "4. Đề xuất và khuyến nghị:\n"
            "   - Giải pháp tối ưu\n"
            "   - Cải thiện hiệu quả\n"
            "   - Kế hoạch hành động\n\n"
            "5. Theo dõi và đánh giá:\n"
            "   - Chỉ số theo dõi\n"
            "   - Thời gian đánh giá\n"
            "   - Mục tiêu cần đạt\n\n"
            "Trả lời cần:\n"
            "- Dựa trên dữ liệu thực tế\n"
            "- Phân tích chi tiết và logic\n"
            "- Đề xuất giải pháp khả thi\n"
            "- Sử dụng ngôn ngữ chuyên nghiệp\n"
            "- Cung cấp ví dụ cụ thể"
        )

    def _get_response_title(self, query: str) -> str:
        return f"Phân tích dữ liệu - {query.split()[0] if query else 'Hỗ trợ'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết về vấn đề này. Vui lòng liên hệ bộ phận hỗ trợ shop để được tư vấn cụ thể hơn."

class Analytics:
    def __init__(self, db: Session):
        self.db = db
        self.agent = AnalyticsAgent()
        self.analytics_repository = AnalyticsRepository(db)

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytics request"""
        try:
            shop_id = request.get('shop_id')
            if not shop_id:
                return {
                    "message": "Không tìm thấy thông tin shop.",
                    "type": "error"
                }

            # Lấy thông tin phân tích của shop
            analytics_data = await self.analytics_repository.get_by_shop(shop_id)
            if not analytics_data:
                return {
                    "message": "Shop chưa có dữ liệu phân tích nào.",
                    "type": "text",
                    "data": {
                        "total_revenue": 0,
                        "total_orders": 0,
                        "total_customers": 0,
                        "metrics": {}
                    }
                }

            # Format thông tin phân tích
            metrics = {
                "revenue": {
                    "daily": analytics_data.get('daily_revenue', 0),
                    "weekly": analytics_data.get('weekly_revenue', 0),
                    "monthly": analytics_data.get('monthly_revenue', 0),
                    "total": analytics_data.get('total_revenue', 0)
                },
                "orders": {
                    "daily": analytics_data.get('daily_orders', 0),
                    "weekly": analytics_data.get('weekly_orders', 0),
                    "monthly": analytics_data.get('monthly_orders', 0),
                    "total": analytics_data.get('total_orders', 0)
                },
                "customers": {
                    "new": analytics_data.get('new_customers', 0),
                    "returning": analytics_data.get('returning_customers', 0),
                    "total": analytics_data.get('total_customers', 0)
                },
                "products": {
                    "top_selling": analytics_data.get('top_selling_products', []),
                    "low_stock": analytics_data.get('low_stock_products', []),
                    "total": analytics_data.get('total_products', 0)
                }
            }

            # Tạo response
            response = {
                "message": f"Thông tin phân tích của shop:\n\n"
                          f"1. Doanh thu:\n"
                          f"   - Hôm nay: {metrics['revenue']['daily']:,}đ\n"
                          f"   - Tuần này: {metrics['revenue']['weekly']:,}đ\n"
                          f"   - Tháng này: {metrics['revenue']['monthly']:,}đ\n"
                          f"   - Tổng cộng: {metrics['revenue']['total']:,}đ\n\n"
                          f"2. Đơn hàng:\n"
                          f"   - Hôm nay: {metrics['orders']['daily']}\n"
                          f"   - Tuần này: {metrics['orders']['weekly']}\n"
                          f"   - Tháng này: {metrics['orders']['monthly']}\n"
                          f"   - Tổng cộng: {metrics['orders']['total']}\n\n"
                          f"3. Khách hàng:\n"
                          f"   - Khách mới: {metrics['customers']['new']}\n"
                          f"   - Khách quay lại: {metrics['customers']['returning']}\n"
                          f"   - Tổng số: {metrics['customers']['total']}",
                "type": "text",
                "data": {
                    "total_revenue": metrics['revenue']['total'],
                    "total_orders": metrics['orders']['total'],
                    "total_customers": metrics['customers']['total'],
                    "metrics": metrics
                }
            }

            # Thêm thông tin chi tiết nếu có yêu cầu cụ thể
            message = request.get('message', '').lower()
            if 'chi tiết' in message or 'detail' in message:
                response['message'] += f"\n\n4. Sản phẩm:\n"
                if metrics['products']['top_selling']:
                    response['message'] += f"   - Sản phẩm bán chạy:\n" + "\n".join([
                        f"     + {product['name']}: {product['quantity']} đơn vị"
                        for product in metrics['products']['top_selling'][:5]
                    ])
                if metrics['products']['low_stock']:
                    response['message'] += f"\n   - Sản phẩm sắp hết hàng:\n" + "\n".join([
                        f"     + {product['name']}: {product['current_stock']} đơn vị"
                        for product in metrics['products']['low_stock'][:5]
                    ])

            return response

        except Exception as e:
            logger.error(f"Error processing analytics request: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for process method to maintain backward compatibility"""
        return await self.process(request)

@router.post("/query")
async def query_analytics(request: ChatMessageRequest):
    try:
        analytics = Analytics(Session())
        # Convert to ShopRequest format
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
        response = await analytics.process(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_analytics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_analytics():
    """List all analytics data for a shop"""
    return {"message": "List analytics endpoint"} 