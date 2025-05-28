from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.message import MessageRepository
from models.chats import ChatMessageCreate
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models.products import Product
from models.orders import Order
from models.reviews import Review
from models.inventories import Inventory
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
    def __init__(self, db: Session, shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.agent = AnalyticsAgent(shop_id)

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytics request."""
        try:
            shop_id = request.get('shop_id') or self.shop_id
            message = request.get('message', '').lower()
            chat_history = request.get('chat_history', '')
            
            if not shop_id:
                return {"message": "Không tìm thấy thông tin shop.", "type": "error"}

            try:
                # Lấy thông tin phân tích của shop
                analytics_data = await self._get_shop_analytics(shop_id)
            except Exception as e:
                # Rollback transaction nếu có lỗi
                self.db.rollback()
                logger.error(f"Error getting analytics data: {str(e)}")
                return {
                    "message": "Không thể lấy dữ liệu phân tích. Vui lòng thử lại sau.",
                    "type": "error",
                    "error": str(e)
                }

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

            # Tạo prompt cho LLM để phân tích yêu cầu và tạo phản hồi
            prompt = f"""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce.
Hãy phân tích yêu cầu của người bán và tạo phản hồi phù hợp dựa trên dữ liệu phân tích.

Yêu cầu của người bán: "{message}"

Dữ liệu phân tích của shop:
1. Doanh thu:
   - Hôm nay: {analytics_data['revenue']['daily']:,}đ
   - Tuần này: {analytics_data['revenue']['weekly']:,}đ
   - Tháng này: {analytics_data['revenue']['monthly']:,}đ
   - Tổng cộng: {analytics_data['revenue']['total']:,}đ

2. Đơn hàng:
   - Hôm nay: {analytics_data['orders']['daily']}
   - Tuần này: {analytics_data['orders']['weekly']}
   - Tháng này: {analytics_data['orders']['monthly']}
   - Tổng cộng: {analytics_data['orders']['total']}

3. Khách hàng:
   - Khách mới: {analytics_data['customers']['new']}
   - Khách quay lại: {analytics_data['customers']['returning']}
   - Tổng số: {analytics_data['customers']['total']}

4. Sản phẩm:
   - Tổng số sản phẩm: {analytics_data['products']['total']}
   - Sản phẩm bán chạy: {[p['name'] for p in analytics_data['products']['top_selling']]}
   - Sản phẩm sắp hết hàng: {[p['name'] for p in analytics_data['products']['low_stock']]}
   - Sản phẩm tồn kho nhiều: {[p['name'] for p in analytics_data['products']['high_stock']]}

Hãy phân tích yêu cầu và tạo phản hồi theo cấu trúc sau:
1. Phân tích yêu cầu:
   - Mục đích chính
   - Các vấn đề cần giải quyết
   - Dữ liệu liên quan

2. Phản hồi chi tiết:
   - Thông tin thực tế từ dữ liệu
   - Phân tích và đánh giá
   - Đề xuất giải pháp

3. Các bước thực hiện:
   - Hướng dẫn cụ thể
   - Lưu ý quan trọng
   - Kết quả mong đợi

Trả lời cần:
- Chuyên nghiệp và dễ hiểu
- Dựa trên dữ liệu thực tế
- Đề xuất giải pháp khả thi
- Cung cấp ví dụ cụ thể
- Sử dụng emoji phù hợp
- Định dạng markdown rõ ràng"""

            # Tạo response sử dụng assistant
            response = await self.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "message": response if response else "Xin lỗi, tôi không thể tạo phản hồi phù hợp. Vui lòng thử lại sau.",
                "type": "text",
                "data": analytics_data
            }

        except Exception as e:
            logger.error(f"Error processing analytics request: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

    async def _get_shop_analytics(self, shop_id: int) -> Dict[str, Any]:
        """Get analytics data for a shop directly from database tables."""
        try:
            # Get date ranges
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = datetime(now.year, now.month, 1)

            # Get orders
            orders = self.db.query(Order).filter(Order.seller_id == shop_id).all()
            daily_orders = [o for o in orders if o.created_at >= today_start]
            weekly_orders = [o for o in orders if o.created_at >= week_start]
            monthly_orders = [o for o in orders if o.created_at >= month_start]

            # Calculate revenue
            daily_revenue = sum(o.total_amount for o in daily_orders)
            weekly_revenue = sum(o.total_amount for o in weekly_orders)
            monthly_revenue = sum(o.total_amount for o in monthly_orders)
            total_revenue = sum(o.total_amount for o in orders)

            # Get products
            products = self.db.query(Product).filter(Product.shop_id == shop_id).all()
            inventories = self.db.query(Inventory).filter(
                Inventory.product_id.in_([p.product_id for p in products])
            ).all()
            inventory_map = {inv.product_id: inv for inv in inventories}

            # Get top selling and stock products
            top_selling = sorted(products, key=lambda x: x.quantity_sold, reverse=True)[:5]
            low_stock = [p for p in products if inventory_map.get(p.product_id) and inventory_map[p.product_id].current_stock < 10]
            high_stock = [p for p in products if inventory_map.get(p.product_id) and inventory_map[p.product_id].current_stock > 50]
            
            # Get highest and lowest stock products
            products_with_stock = [(p, inventory_map.get(p.product_id)) for p in products if inventory_map.get(p.product_id)]
            highest_stock = sorted(products_with_stock, key=lambda x: x[1].current_stock, reverse=True)[:5]
            lowest_stock = sorted(products_with_stock, key=lambda x: x[1].current_stock)[:5]

            # Get customer metrics
            customer_ids = set(o.customer_id for o in orders)
            customer_order_count = {}
            for order in orders:
                customer_order_count[order.customer_id] = customer_order_count.get(order.customer_id, 0) + 1
            returning_customers = sum(1 for count in customer_order_count.values() if count > 1)

            # Get reviews
            reviews = self.db.query(Review).filter(Review.shop_id == shop_id).all()
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

            return {
                "revenue": {
                    "daily": daily_revenue,
                    "weekly": weekly_revenue,
                    "monthly": monthly_revenue,
                    "total": total_revenue
                },
                "orders": {
                    "daily": len(daily_orders),
                    "weekly": len(weekly_orders),
                    "monthly": len(monthly_orders),
                    "total": len(orders)
                },
                "customers": {
                    "new": len(customer_ids) - returning_customers,
                    "returning": returning_customers,
                    "total": len(customer_ids)
                },
                "products": {
                    "top_selling": [{"name": p.name, "quantity": p.quantity_sold} for p in top_selling],
                    "low_stock": [{"name": p.name, "current_stock": inventory_map[p.product_id].current_stock} for p in low_stock],
                    "high_stock": [{"name": p.name, "current_stock": inventory_map[p.product_id].current_stock} for p in high_stock],
                    "highest_stock": [{"name": p[0].name, "current_stock": p[1].current_stock} for p in highest_stock],
                    "lowest_stock": [{"name": p[0].name, "current_stock": p[1].current_stock} for p in lowest_stock],
                    "total": len(products)
                }
            }
        except Exception as e:
            logger.error(f"Error getting shop analytics: {str(e)}")
            raise e

    async def _handle_inventory_recommendation(self, message: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory recommendation request using LLM for detailed analysis."""
        if not analytics_data or not analytics_data.get('products'):
            return {
                "message": "❌ **Lỗi**: Không tìm thấy thông tin về sản phẩm tồn kho.",
                "type": "error"
            }

        # Tạo prompt chi tiết cho LLM
        prompt = f"""Bạn là một chuyên gia tư vấn kinh doanh thương mại điện tử chuyên nghiệp.
Hãy phân tích và đề xuất chiến lược bán hàng cho các sản phẩm tồn kho dựa trên dữ liệu thực tế.

Yêu cầu của người bán: "{message}"

Dữ liệu phân tích của shop:
1. Doanh thu:
   - Hôm nay: {analytics_data['revenue']['daily']:,}đ
   - Tuần này: {analytics_data['revenue']['weekly']:,}đ
   - Tháng này: {analytics_data['revenue']['monthly']:,}đ
   - Tổng cộng: {analytics_data['revenue']['total']:,}đ

2. Đơn hàng:
   - Hôm nay: {analytics_data['orders']['daily']}
   - Tuần này: {analytics_data['orders']['weekly']}
   - Tháng này: {analytics_data['orders']['monthly']}
   - Tổng cộng: {analytics_data['orders']['total']}

3. Khách hàng:
   - Khách mới: {analytics_data['customers']['new']}
   - Khách quay lại: {analytics_data['customers']['returning']}
   - Tổng số: {analytics_data['customers']['total']}

4. Sản phẩm:
   - Tổng số sản phẩm: {analytics_data['products']['total']}
   - Sản phẩm bán chạy: {[p['name'] for p in analytics_data['products']['top_selling']]}
   - Sản phẩm sắp hết hàng: {[p['name'] for p in analytics_data['products']['low_stock']]}
   - Sản phẩm tồn kho nhiều: {[p['name'] for p in analytics_data['products']['high_stock']]}
   - Sản phẩm tồn kho cao nhất: {[p['name'] for p in analytics_data['products']['highest_stock']]}
   - Sản phẩm tồn kho thấp nhất: {[p['name'] for p in analytics_data['products']['lowest_stock']]}

Hãy phân tích và đề xuất theo cấu trúc sau:

1. 📊 **Phân tích tình hình**:
   - Đánh giá tổng quan về sản phẩm tồn kho
   - Phân tích điểm mạnh của từng sản phẩm
   - Xác định cơ hội thị trường
   - Đánh giá tiềm năng bán hàng

2. 🎯 **Chiến lược bán hàng**:
   - Đề xuất chiến lược cho từng sản phẩm
   - Kế hoạch tiếp cận khách hàng
   - Cách thức quảng bá sản phẩm
   - Chiến lược giá và khuyến mãi

3. 📈 **Kế hoạch thực hiện**:
   - Các bước thực hiện cụ thể
   - Thời gian và lộ trình
   - Nguồn lực cần thiết
   - Chỉ số đánh giá hiệu quả

4. 💡 **Đề xuất sáng tạo**:
   - Ý tưởng đóng gói sản phẩm
   - Cách tạo sự khác biệt
   - Chiến lược tạo giá trị gia tăng
   - Cơ hội phát triển mới

5. ⚠️ **Lưu ý quan trọng**:
   - Các rủi ro cần tránh
   - Điểm cần lưu ý khi thực hiện
   - Cách xử lý tình huống đặc biệt
   - Kế hoạch dự phòng

Trả lời cần:
- Chuyên nghiệp và chi tiết
- Tập trung vào điểm mạnh của sản phẩm
- Đề xuất giải pháp khả thi và sáng tạo
- Cung cấp ví dụ cụ thể
- Sử dụng emoji phù hợp
- Định dạng markdown rõ ràng
- Tập trung vào lợi ích của người bán"""

        # Tạo response sử dụng assistant
        response = await self.assistant.a_generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "message": response if response else "Xin lỗi, tôi không thể tạo phản hồi phù hợp. Vui lòng thử lại sau.",
            "type": "inventory_recommendation",
            "data": {
                "products": analytics_data['products'],
                "analytics_data": analytics_data
            }
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