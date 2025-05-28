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
from models.order_details import OrderDetail
from models.reviews import Review
from models.inventories import Inventory
import traceback
from decimal import Decimal
import openai

# Custom JSON encoder để xử lý Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

router = APIRouter(prefix="/shop/analytics", tags=["Shop Analytics"])

class AnalyticsAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None, db: Session = None):
        super().__init__(
            shop_id=shop_id,
            name="AnalyticsAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và hướng dẫn cho người bán về phân tích dữ liệu và báo cáo.

Nhiệm vụ của bạn:
1. Phân tích dữ liệu bán hàng
2. Tạo báo cáo thống kê
3. Đề xuất cải thiện
4. Dự đoán xu hướng
5. Phân tích đánh giá sản phẩm

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

6. Phân tích đánh giá:
   - Điểm đánh giá trung bình
   - Phân tích cảm xúc
   - Tổng hợp ý kiến
   - Đề xuất cải thiện
   - Theo dõi phản hồi

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
        self.db = db

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytics request."""
        try:
            message = request.get('message', '')
            shop_id = request.get('shop_id')
            chat_history = request.get('chat_history', '')
            analytics_data = request.get('analytics_data', {})
            
            if not shop_id:
                return {
                    "message": "Không tìm thấy thông tin shop.",
                    "type": "error"
                }

            # Kiểm tra nếu là yêu cầu về đánh giá sản phẩm
            if "đánh giá" in message.lower() or "review" in message.lower():
                return await self._handle_review_analysis(request)

            # Kiểm tra nếu là khiếu nại của khách hàng
            complaint_keywords = [
                "tệ", "kém", "không tốt", "chất lượng kém", "đánh giá thấp", 
                "phàn nàn", "khiếu nại", "kém hơn", "tệ hơn", "chất lượng thấp",
                "so sánh", "shop khác", "cửa hàng khác", "đối thủ"
            ]
            
            # Kiểm tra nếu message chứa từ khóa khiếu nại
            if any(keyword in message.lower() for keyword in complaint_keywords):
                # Chuyển hướng sang customer service mà không thêm thông tin
                from .customer_service import CustomerService
                customer_service = CustomerService(self.db, shop_id)
                return await customer_service.process({
                    "message": message,
                    "shop_id": shop_id
                })

            # Tạo prompt cho LLM
            prompt = self._build_prompt(message, f"Shop ID: {shop_id}\nChat History:\n{chat_history}\nAnalytics Data:\n{json.dumps(analytics_data, indent=2, ensure_ascii=False, cls=DecimalEncoder)}")
            
            # Tạo response sử dụng assistant
            response = await self.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not response:
                return {
                    "message": self._get_fallback_response(),
                    "type": "text"
                }
            
            # Đảm bảo response là string
            if not isinstance(response, str):
                response = str(response)
            
            return {
                "message": response,
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
            "- Cung cấp ví dụ cụ thể\n"
            "- Thêm emoji phù hợp để tăng tính trực quan\n"
            "- Định dạng số liệu dễ đọc (ví dụ: 1,000,000)\n"
            "- Kết thúc bằng lời khuyến khích tích cực"
        )

    def _get_response_title(self, query: str) -> str:
        return f"Phân tích dữ liệu - {query.split()[0] if query else 'Hỗ trợ'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết về vấn đề này. Vui lòng liên hệ bộ phận hỗ trợ shop để được tư vấn cụ thể hơn."

    async def _handle_review_analysis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product review analysis request."""
        try:
            shop_id = request.get('shop_id')
            message = request.get('message', '')
            
            # Lấy thông tin đánh giá của tất cả sản phẩm trong shop
            reviews = self.db.query(
                Review.product_id,
                Product.name.label('product_name'),
                func.avg(Review.rating).label('average_rating'),
                func.count(Review.review_id).label('total_reviews')
            ).join(
                Product, Review.product_id == Product.product_id
            ).filter(
                Product.seller_id == shop_id
            ).group_by(
                Review.product_id,
                Product.name
            ).all()

            if not reviews:
                return {
                    "message": "Shop của bạn chưa có đánh giá nào từ khách hàng.",
                    "type": "text"
                }

            # Tính toán các chỉ số đánh giá
            total_reviews = sum(r.total_reviews for r in reviews)
            average_rating = sum(r.average_rating * r.total_reviews for r in reviews) / total_reviews
            sentiment_score = average_rating / 5

            # Sắp xếp sản phẩm theo điểm đánh giá
            sorted_products = sorted(reviews, key=lambda x: x.average_rating, reverse=True)
            top_products = sorted_products[:3]  # Top 3 sản phẩm được đánh giá cao nhất
            bottom_products = sorted_products[-3:]  # 3 sản phẩm có đánh giá thấp nhất

            # Tạo prompt cho LLM
            prompt = f"""Bạn là chuyên gia phân tích đánh giá sản phẩm của sàn thương mại điện tử IUH-Ecommerce.
Hãy phân tích và tổng hợp các đánh giá thực tế từ người dùng để tư vấn cho người bán.

Yêu cầu của người bán: {message}

Thông tin đánh giá shop:
- Tổng số đánh giá: {total_reviews}
- Điểm đánh giá trung bình: {average_rating:.2f}/5
- Chỉ số cảm xúc: {sentiment_score:.2f}

Top 3 sản phẩm được đánh giá cao nhất:
{chr(10).join([f"- {p.product_name}: {p.average_rating:.2f}/5 ({p.total_reviews} đánh giá)" for p in top_products])}

3 sản phẩm cần cải thiện:
{chr(10).join([f"- {p.product_name}: {p.average_rating:.2f}/5 ({p.total_reviews} đánh giá)" for p in bottom_products])}

Yêu cầu:
1. Mở đầu bằng lời chào và cảm ơn người bán
2. Phân tích tổng quan về đánh giá:
   - Điểm đánh giá trung bình và ý nghĩa
   - Số lượng đánh giá và độ tin cậy
   - Phân bố đánh giá theo mức độ
3. Phân tích sản phẩm được đánh giá cao:
   - Điểm mạnh của từng sản phẩm
   - Lý do được đánh giá cao
   - Cách duy trì chất lượng
4. Phân tích sản phẩm cần cải thiện:
   - Điểm yếu của từng sản phẩm
   - Nguyên nhân đánh giá thấp
   - Đề xuất cải thiện
5. Đề xuất chiến lược:
   - Cách duy trì điểm mạnh
   - Kế hoạch cải thiện điểm yếu
   - Chiến lược tăng đánh giá tích cực
6. Kết luận và khuyến nghị:
   - Tóm tắt tình hình
   - Đề xuất ưu tiên
   - Lộ trình cải thiện

Lưu ý:
- Sử dụng ngôn ngữ chuyên nghiệp và thân thiện
- Đưa ra số liệu cụ thể và dễ hiểu
- Tập trung vào giải pháp thực tế
- Thêm emoji phù hợp để tăng tính trực quan
- Kết thúc bằng lời khuyến khích tích cực"""

            # Tạo response sử dụng assistant
            response = await self.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            if not response:
                return {
                    "message": self._get_fallback_response(),
                    "type": "text"
                }

            return {
                "message": response,
                "type": "text",
                "data": {
                    "total_reviews": total_reviews,
                    "average_rating": float(average_rating),
                    "sentiment_score": float(sentiment_score),
                    "top_products": [
                        {
                            "product_name": p.product_name,
                            "average_rating": float(p.average_rating),
                            "total_reviews": p.total_reviews
                        }
                        for p in top_products
                    ],
                    "bottom_products": [
                        {
                            "product_name": p.product_name,
                            "average_rating": float(p.average_rating),
                            "total_reviews": p.total_reviews
                        }
                        for p in bottom_products
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error in _handle_review_analysis: {str(e)}")
            return {
                "message": "Không thể phân tích đánh giá sản phẩm. Vui lòng thử lại sau.",
                "type": "error"
            }

    async def analyze_intent(self, message: str, chat_history: str = "") -> dict:
        """Use GPT-4o-mini to analyze user intent and context."""
        prompt = f"""
Bạn là AI phân tích mục đích và ngữ cảnh tin nhắn của người dùng trong hệ thống quản lý shop. Hãy trả lời JSON với các trường:
{{
  "intent": "deny_complaint" | "real_complaint" | "product_info" | "chitchat" | "top_inventory_high" | "top_inventory_low" | "inventory_below_threshold" | "inventory_above_threshold" | "other",
  "entities": [{{"type": "threshold", "value": <số lượng nếu có, ví dụ: 1000, 3000, ...>}}, ...],
  "sentiment": "positive" | "neutral" | "negative",
  "reason": "Giải thích ngắn gọn vì sao bạn chọn intent này"
}}
Ngữ cảnh chat (nếu có): {chat_history}
Tin nhắn mới: {message}
"""
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.2
        )
        import json as pyjson
        content = response["choices"][0]["message"]["content"]
        try:
            result = pyjson.loads(content)
        except Exception:
            # fallback: try to extract JSON from text
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                result = pyjson.loads(match.group())
            else:
                result = {"intent": "other", "entities": [], "sentiment": "neutral", "reason": "Không phân tích được"}
        return result

class Analytics:
    def __init__(self, db: Session, shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.agent = AnalyticsAgent(shop_id=shop_id, db=db)

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytics request with intent analysis."""
        try:
            shop_id = request.get('shop_id') or self.shop_id
            message = request.get('message', '')
            chat_history = request.get('chat_history', '')
            if not shop_id:
                return {
                    "message": "Không tìm thấy thông tin shop.",
                    "type": "error"
                }

            # Phân tích intent bằng GPT-4o-mini
            intent_result = await self.agent.analyze_intent(message, chat_history)
            intent = intent_result.get("intent", "other")

            if intent == "deny_complaint":
                return {
                    "message": "Tôi đã ghi nhận, hiện tại không có khách hàng nào phàn nàn trực tiếp với bạn. Nếu có phản hồi cụ thể, bạn hãy cung cấp để tôi hỗ trợ xử lý.",
                    "type": "text"
                }
            elif intent == "real_complaint":
                from .customer_service import CustomerService
                customer_service = CustomerService(self.db, shop_id)
                return await customer_service.process({
                    "message": message,
                    "shop_id": shop_id
                })
            elif intent == "product_info":
                from .product_management import ProductManagement
                product_agent = ProductManagement(self.db, shop_id)
                return await product_agent.process({
                    "message": message,
                    "shop_id": shop_id
                })
            elif intent == "chitchat":
                return {
                    "message": "Cảm ơn bạn đã trò chuyện! Nếu bạn cần hỗ trợ gì về shop, hãy đặt câu hỏi nhé!",
                    "type": "text"
                }
            elif intent == "top_inventory_high":
                # Chỉ trả về danh sách sản phẩm tồn kho nhiều nhất
                analytics_data = await self._get_shop_analytics(shop_id)
                inventory_data = analytics_data.get("inventory", [])
                products_data = {p["product_id"]: p for p in analytics_data.get("products", [])}
                sorted_inventory = sorted(
                    inventory_data,
                    key=lambda x: x.get("current_stock", 0),
                    reverse=True
                )
                top_5_high_stock = sorted_inventory[:5]
                message_lines = ["Top 5 sản phẩm tồn kho nhiều nhất:"]
                for idx, item in enumerate(top_5_high_stock, 1):
                    p = products_data.get(item["product_id"], {})
                    message_lines.append(f"{idx}. {p.get('name', 'Unknown')}: {item['current_stock']:,} sản phẩm, Giá: {p.get('price', 0):,.0f}₫, Đã bán: {p.get('quantity_sold', 0):,}, Đánh giá: {p.get('average_rating', 'N/A')}/5")
                return {
                    "message": "\n".join(message_lines),
                    "type": "text",
                    "data": top_5_high_stock
                }
            elif intent == "top_inventory_low":
                # Chỉ trả về danh sách sản phẩm tồn kho ít nhất
                analytics_data = await self._get_shop_analytics(shop_id)
                inventory_data = analytics_data.get("inventory", [])
                products_data = {p["product_id"]: p for p in analytics_data.get("products", [])}
                # Sắp xếp tăng dần theo tồn kho
                sorted_inventory = sorted(
                    inventory_data,
                    key=lambda x: x.get("current_stock", 0)
                )
                top_5_low_stock = sorted_inventory[:5]
                message_lines = ["Top 5 sản phẩm còn ít nhất trong kho:"]
                for idx, item in enumerate(top_5_low_stock, 1):
                    p = products_data.get(item["product_id"], {})
                    message_lines.append(
                        f"{idx}. {p.get('name', 'Unknown')}: {item['current_stock']:,} sản phẩm, "
                        f"Giá: {p.get('price', 0):,.0f}₫, Đã bán: {p.get('quantity_sold', 0):,}, "
                        f"Đánh giá: {p.get('average_rating', 'N/A')}/5"
                    )
                return {
                    "message": "\n".join(message_lines),
                    "type": "text",
                    "data": top_5_low_stock
                }
            elif intent == "inventory_below_threshold":
                # Lọc sản phẩm tồn kho dưới ngưỡng do người dùng đặt ra
                threshold = None
                for ent in intent_result.get("entities", []):
                    if ent.get("type") == "threshold":
                        try:
                            threshold = int(ent.get("value"))
                        except Exception:
                            pass
                if threshold is None:
                    return {"message": "Bạn vui lòng cung cấp ngưỡng tồn kho cần tra cứu.", "type": "text"}
                analytics_data = await self._get_shop_analytics(shop_id)
                inventory_data = analytics_data.get("inventory", [])
                products_data = {p["product_id"]: p for p in analytics_data.get("products", [])}
                filtered = [item for item in inventory_data if item.get("current_stock", 0) < threshold]
                message_lines = [f"Sản phẩm tồn kho dưới {threshold}:"]
                for idx, item in enumerate(filtered, 1):
                    p = products_data.get(item["product_id"], {})
                    message_lines.append(f"{idx}. {p.get('name', 'Unknown')}: {item['current_stock']:,} sản phẩm, Giá: {p.get('price', 0):,.0f}₫, Đã bán: {p.get('quantity_sold', 0):,}, Đánh giá: {p.get('average_rating', 'N/A')}/5")
                return {
                    "message": "\n".join(message_lines) if filtered else f"Không có sản phẩm nào tồn kho dưới {threshold}.",
                    "type": "text",
                    "data": filtered
                }
            elif intent == "inventory_above_threshold":
                # Lọc sản phẩm tồn kho trên ngưỡng do người dùng đặt ra
                threshold = None
                for ent in intent_result.get("entities", []):
                    if ent.get("type") == "threshold":
                        try:
                            threshold = int(ent.get("value"))
                        except Exception:
                            pass
                if threshold is None:
                    return {"message": "Bạn vui lòng cung cấp ngưỡng tồn kho cần tra cứu.", "type": "text"}
                analytics_data = await self._get_shop_analytics(shop_id)
                inventory_data = analytics_data.get("inventory", [])
                products_data = {p["product_id"]: p for p in analytics_data.get("products", [])}
                filtered = [item for item in inventory_data if item.get("current_stock", 0) > threshold]
                message_lines = [f"Sản phẩm tồn kho trên {threshold}:"]
                for idx, item in enumerate(filtered, 1):
                    p = products_data.get(item["product_id"], {})
                    message_lines.append(f"{idx}. {p.get('name', 'Unknown')}: {item['current_stock']:,} sản phẩm, Giá: {p.get('price', 0):,.0f}₫, Đã bán: {p.get('quantity_sold', 0):,}, Đánh giá: {p.get('average_rating', 'N/A')}/5")
                return {
                    "message": "\n".join(message_lines) if filtered else f"Không có sản phẩm nào tồn kho trên {threshold}.",
                    "type": "text",
                    "data": filtered
                }
            # fallback: xử lý như cũ
            try:
                # Lấy thông tin phân tích của shop
                analytics_data = await self._get_shop_analytics(shop_id)
            except Exception as e:
                # Rollback transaction nếu có lỗi
                self.db.rollback()
                logger.error(f"Error getting analytics data: {str(e)}")
                return {
                    "message": "Không thể lấy dữ liệu phân tích. Vui lòng thử lại sau.",
                    "type": "error"
                }

            if not analytics_data:
                return {
                    "message": "Shop chưa có dữ liệu phân tích nào.",
                    "type": "text"
                }

            # Xử lý câu hỏi về tồn kho
            if "tồn kho" in message or "tồn" in message:
                inventory_data = analytics_data.get("inventory", [])
                products_data = {p["product_id"]: p for p in analytics_data.get("products", [])}
                
                # Sắp xếp sản phẩm theo số lượng tồn kho
                sorted_inventory = sorted(
                    inventory_data,
                    key=lambda x: x.get("current_stock", 0),
                    reverse=True
                )
                
                # Lấy top 5 sản phẩm tồn kho nhiều nhất
                top_5_high_stock = sorted_inventory[:5]
                # Lấy top 5 sản phẩm tồn kho ít nhất
                top_5_low_stock = sorted_inventory[-5:][::-1]
                
                # Tạo message phân tích tồn kho
                inventory_message = f"""📊 **Tóm tắt Thông tin Cửa hàng IUH-Ecommerce**

📦 **Thống kê Sản phẩm**:
- Tổng số sản phẩm: {analytics_data.get('metrics', {}).get('total_products', 0):,} sản phẩm
- Sản phẩm còn tồn kho: {analytics_data.get('metrics', {}).get('products_in_stock', 0):,} sản phẩm
- Sản phẩm đã bán: {analytics_data.get('metrics', {}).get('total_sold', 0):,} sản phẩm
- Giá trị tồn kho: {analytics_data.get('metrics', {}).get('total_inventory_value', 0):,.0f} VNĐ

💰 **Doanh thu**:
- Tổng doanh thu: {analytics_data.get('total_revenue', 0):,.0f} VNĐ
- Giá trị trung bình mỗi đơn hàng: {analytics_data.get('metrics', {}).get('average_order_value', 0):,.0f} VNĐ

⭐ **Đánh giá**:
- Điểm trung bình: {analytics_data.get('metrics', {}).get('average_rating', 0):.1f}/5
- Tổng số đánh giá: {analytics_data.get('metrics', {}).get('total_reviews', 0):,} đánh giá

📈 **Hiệu suất**:
- Tỷ lệ chuyển đổi: {analytics_data.get('metrics', {}).get('conversion_rate', 0):.1f}%

📊 **Phân tích Tồn kho**:

🔴 **Top 5 sản phẩm tồn kho nhiều nhất**:
{chr(10).join([f"- {products_data.get(item['product_id'], {}).get('name', 'Unknown')}: {item['current_stock']:,} sản phẩm" for item in top_5_high_stock])}

⚠️ **Top 5 sản phẩm tồn kho ít nhất**:
{chr(10).join([f"- {products_data.get(item['product_id'], {}).get('name', 'Unknown')}: {item['current_stock']:,} sản phẩm" for item in top_5_low_stock])}

💡 **Đề xuất**:
- Cân nhắc giảm giá hoặc khuyến mãi cho các sản phẩm tồn kho nhiều
- Kiểm tra và nhập thêm hàng cho các sản phẩm tồn kho ít
- Theo dõi thường xuyên mức tồn kho để đảm bảo cân bằng

📝 **Kết luận**:
Cửa hàng hiện đang giữ {analytics_data.get('metrics', {}).get('products_in_stock', 0):,} sản phẩm trong kho với tổng giá trị tồn kho là {analytics_data.get('metrics', {}).get('total_inventory_value', 0):,.0f} VNĐ và đã đạt doanh thu lên tới {analytics_data.get('total_revenue', 0):,.0f} VNĐ từ {analytics_data.get('metrics', {}).get('total_sold', 0):,} sản phẩm đã bán. Với điểm đánh giá trung bình đạt {analytics_data.get('metrics', {}).get('average_rating', 0):.1f}/5, cửa hàng thể hiện tiềm năng tốt nhưng vẫn cần cải thiện để thực hiện tốt hơn trong tương lai."""

                return {
                    "message": inventory_message,
                    "type": "text",
                    "data": {
                        "high_stock": top_5_high_stock,
                        "low_stock": top_5_low_stock,
                        "inventory": inventory_data
                    }
                }

            # Tạo response sử dụng agent cho các câu hỏi khác
            response = await self.agent.process({
                "message": message,
                "shop_id": shop_id,
                "chat_history": chat_history,
                "analytics_data": analytics_data
            })

            if not response:
                return {
                    "message": "Không thể tạo phản hồi. Vui lòng thử lại sau.",
                    "type": "error"
                }

            # Chuyển đổi response sang định dạng chuẩn
            if isinstance(response, dict):
                # Tạo message tóm tắt thông tin quan trọng
                summary_message = f"""📊 **Tóm tắt và Phân tích Tình hình Cửa hàng**

📦 **Thống kê Sản phẩm**:
- Tổng số sản phẩm: {analytics_data.get('metrics', {}).get('total_products', 0):,} sản phẩm
- Sản phẩm còn tồn kho: {analytics_data.get('metrics', {}).get('products_in_stock', 0):,} sản phẩm
- Sản phẩm đã bán: {analytics_data.get('metrics', {}).get('total_sold', 0):,} sản phẩm

💰 **Doanh thu**:
- Tổng doanh thu: {analytics_data.get('total_revenue', 0):,.0f} VNĐ từ {analytics_data.get('total_orders', 0):,} đơn hàng
- Giá trị trung bình mỗi đơn hàng: {analytics_data.get('metrics', {}).get('average_order_value', 0):,.0f} VNĐ

⭐ **Đánh giá**:
- Điểm trung bình: {analytics_data.get('metrics', {}).get('average_rating', 0):.1f}/5
- Tổng số đánh giá: {analytics_data.get('metrics', {}).get('total_reviews', 0):,} đánh giá

📈 **Hiệu suất**:
- Tỷ lệ chuyển đổi: {analytics_data.get('metrics', {}).get('conversion_rate', 0):.1f}%
- Giá trị tồn kho: {analytics_data.get('metrics', {}).get('total_inventory_value', 0):,.0f} VNĐ"""

                return {
                    "message": summary_message,
                    "type": "text",
                    "data": {
                        "revenue": analytics_data.get("total_revenue", 0),
                        "orders": analytics_data.get("total_orders", 0),
                        "products": analytics_data.get("products", []),
                        "inventory": analytics_data.get("inventory", []),
                        "metrics": analytics_data.get("metrics", {})
                    }
                }
            else:
                return {
                    "message": "Không thể tạo phản hồi. Vui lòng thử lại sau.",
                    "type": "error"
                }

        except Exception as e:
            logger.error(f"Error in Analytics.process: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu phân tích. Vui lòng thử lại sau.",
                "type": "error"
            }

    async def _get_shop_analytics(self, shop_id: int) -> Dict[str, Any]:
        """Get analytics data for a shop."""
        try:
            # Lấy tổng số sản phẩm
            total_products = self.db.query(func.count(Product.product_id)).filter(
                Product.seller_id == shop_id
            ).scalar() or 0

            # Lấy số sản phẩm còn tồn kho (current_stock > 0)
            products_in_stock = self.db.query(func.count(Product.product_id)).join(
                Inventory, Product.product_id == Inventory.product_id
            ).filter(
                Product.seller_id == shop_id,
                Inventory.current_stock > 0
            ).scalar() or 0

            # Lấy thông tin tổng quan
            total_revenue = self.db.query(
                func.sum(Product.quantity_sold * Product.price)
            ).filter(
                Product.seller_id == shop_id
            ).scalar() or 0

            total_orders = self.db.query(func.count(func.distinct(OrderDetail.order_id))).join(
                Product, OrderDetail.product_id == Product.product_id
            ).filter(
                Product.seller_id == shop_id
            ).scalar() or 0

            total_customers = self.db.query(func.count(func.distinct(Order.customer_id))).join(
                OrderDetail, Order.order_id == OrderDetail.order_id
            ).join(
                Product, OrderDetail.product_id == Product.product_id
            ).filter(
                Product.seller_id == shop_id
            ).scalar() or 0

            # Lấy thông tin sản phẩm
            products = self.db.query(
                Product.product_id,
                Product.name,
                Product.price,
                Product.quantity_sold,
                Inventory.current_stock
            ).outerjoin(
                Inventory, Product.product_id == Inventory.product_id
            ).filter(
                Product.seller_id == shop_id
            ).all()

            # Lấy thông tin tồn kho
            inventory = self.db.query(
                Inventory.product_id,
                Inventory.current_stock,
                Inventory.product_virtual_type,
                Inventory.fulfillment_type
            ).join(
                Product, Inventory.product_id == Product.product_id
            ).filter(
                Product.seller_id == shop_id
            ).all()

            # Lấy thông tin đánh giá
            reviews = self.db.query(
                Review.product_id,
                func.avg(Review.rating).label('average_rating'),
                func.count(Review.review_id).label('total_reviews')
            ).join(
                Product, Review.product_id == Product.product_id
            ).filter(
                Product.seller_id == shop_id
            ).group_by(
                Review.product_id
            ).all()

            # Tính toán tổng số sản phẩm đã bán
            total_sold = sum(p.quantity_sold or 0 for p in products)

            # Tính toán tổng giá trị tồn kho
            total_inventory_value = sum(
                (i.current_stock or 0) * (float(p.price or 0))
                for i in inventory
                for p in products
                if i.product_id == p.product_id
            )

            # Tính toán các metrics
            metrics = {
                "total_products": total_products,
                "products_in_stock": products_in_stock,
                "total_sold": total_sold,
                "total_inventory_value": float(total_inventory_value),
                "average_order_value": float(total_revenue / total_orders if total_orders > 0 else 0),
                "customer_lifetime_value": float(total_revenue / total_customers if total_customers > 0 else 0),
                "conversion_rate": float(total_orders / total_customers * 100 if total_customers > 0 else 0),
                "average_rating": float(sum(r.average_rating for r in reviews) / len(reviews) if reviews else 0),
                "total_reviews": sum(r.total_reviews for r in reviews) if reviews else 0
            }

            return {
                "total_revenue": float(total_revenue),
                "total_orders": total_orders,
                "total_customers": total_customers,
                "products": [
                    {
                        "product_id": p.product_id,
                        "name": p.name,
                        "price": float(p.price or 0),
                        "quantity_sold": p.quantity_sold or 0,
                        "current_stock": p.current_stock or 0
                    }
                    for p in products
                ],
                "inventory": [
                    {
                        "product_id": i.product_id,
                        "current_stock": i.current_stock or 0,
                        "product_virtual_type": i.product_virtual_type,
                        "fulfillment_type": i.fulfillment_type,
                        "status": "low" if i.current_stock and i.current_stock <= 10 else "normal" if i.current_stock and i.current_stock <= 50 else "high"
                    }
                    for i in inventory
                ],
                "reviews": [
                    {
                        "product_id": r.product_id,
                        "average_rating": float(r.average_rating),
                        "total_reviews": r.total_reviews
                    }
                    for r in reviews
                ],
                "metrics": metrics
            }

        except Exception as e:
            logger.error(f"Error in _get_shop_analytics: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def _handle_inventory_recommendation(self, message: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inventory-related recommendations."""
        try:
            # Phân tích tồn kho
            inventory_issues = []
            for item in analytics_data.get("inventory", []):
                if item["current_stock"] <= item["min_stock"]:
                    inventory_issues.append({
                        "product_id": item["product_id"],
                        "issue": "low_stock",
                        "current": item["current_stock"],
                        "min": item["min_stock"]
                    })
                elif item["current_stock"] >= item["max_stock"]:
                    inventory_issues.append({
                        "product_id": item["product_id"],
                        "issue": "overstock",
                        "current": item["current_stock"],
                        "max": item["max_stock"]
                    })

            if not inventory_issues:
                return {
                    "message": "Tồn kho của shop đang ở mức ổn định. Không có vấn đề cần xử lý.",
                    "type": "text"
                }

            # Tạo phản hồi dựa trên các vấn đề tồn kho
            response = "📊 **Phân tích tồn kho**:\n\n"
            for issue in inventory_issues:
                if issue["issue"] == "low_stock":
                    response += f"⚠️ Sản phẩm ID {issue['product_id']} đang ở mức tồn kho thấp:\n"
                    response += f"- Hiện tại: {issue['current']}\n"
                    response += f"- Mức tối thiểu: {issue['min']}\n"
                    response += "→ Cần nhập thêm hàng\n\n"
                else:
                    response += f"ℹ️ Sản phẩm ID {issue['product_id']} đang tồn kho cao:\n"
                    response += f"- Hiện tại: {issue['current']}\n"
                    response += f"- Mức tối đa: {issue['max']}\n"
                    response += "→ Cân nhắc giảm giá hoặc khuyến mãi\n\n"

            return {
                "message": response,
                "type": "text",
                "data": {
                    "inventory_issues": inventory_issues
                }
            }

        except Exception as e:
            logger.error(f"Error in _handle_inventory_recommendation: {str(e)}")
            return {
                "message": "Không thể phân tích tồn kho. Vui lòng thử lại sau.",
                "type": "error"
            }

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a general analytics request."""
        return await self.process(request)

@router.post("/query")
async def query_analytics(request: ChatMessageRequest):
    """Query analytics data."""
    try:
        analytics = Analytics(request.db, request.shop_id)
        response = await analytics.process({
            "message": request.message,
            "shop_id": request.shop_id,
            "chat_history": request.chat_history
        })
        return response
    except Exception as e:
        logger.error(f"Error in query_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_analytics():
    """List available analytics endpoints."""
    return {
        "endpoints": [
            {
                "path": "/query",
                "method": "POST",
                "description": "Query analytics data"
            }
        ]
    } 