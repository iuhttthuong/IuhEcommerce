from fastapi import APIRouter, HTTPException
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.message import MessageRepository
from repositories.products import ProductRepositories
from services.shops import ShopServices
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import traceback
import json

router = APIRouter(prefix="/shop/marketing", tags=["Shop Marketing"])

# System message tối ưu cho GPT-4o-mini
OPTIMAL_SYSTEM_MESSAGE = '''
Bạn là chuyên gia marketing AI cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và giải đáp cho từng shop dựa trên dữ liệu thực tế của shop đó.

YÊU CẦU:
- Luôn ưu tiên phân tích, sử dụng dữ liệu sản phẩm, đánh giá, doanh số, phản hồi khách hàng... của shop để trả lời.
- Trả lời phải cá nhân hóa, tập trung vào shop, không trả lời chung chung hoặc lý thuyết suông.
- Phân tích điểm mạnh/yếu từng sản phẩm, đề xuất chiến lược marketing, khuyến mãi, quảng cáo, chăm sóc khách hàng phù hợp với shop.
- Nếu shop hỏi về xu hướng, chính sách, thị trường... hãy chủ động tìm kiếm thông tin mới nhất trên web, nhưng vẫn phải liên hệ, so sánh, hoặc gợi ý áp dụng thực tế cho shop dựa trên dữ liệu shop cung cấp.
- Luôn trả lời chi tiết, đúng trọng tâm câu hỏi, có ví dụ minh họa, hướng dẫn từng bước nếu cần.
- Nếu dữ liệu shop chưa đủ, hãy hỏi lại để lấy thêm thông tin cần thiết.

CẤU TRÚC TRẢ LỜI (nên tham khảo, không bắt buộc cứng nhắc):
1. Tóm tắt vấn đề & mục tiêu shop
2. Phân tích dữ liệu thực tế của shop (sản phẩm, đánh giá, doanh số...)
3. Đề xuất chiến lược/giải pháp phù hợp, có ví dụ minh họa
4. Hướng dẫn từng bước triển khai (nếu cần)
5. Khuyến nghị cải thiện & lưu ý quan trọng

Tuyệt đối không trả lời chung chung, không bỏ qua dữ liệu shop. Nếu phải dùng thông tin ngoài, hãy luôn liên hệ thực tế shop và giải thích rõ ràng.
'''

class MarketingAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None, db: Session = None):
        super().__init__(
            shop_id=shop_id,
            name="MarketingAgent",
            system_message=OPTIMAL_SYSTEM_MESSAGE
        )
        self.db = db
        self.product_repo = ProductRepositories(db)
        self.shop_info = ShopServices.get(shop_id)
        self.message_repository = MessageRepository()
        self.agent_name = "MarketingAgent"

    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        try:
            products = self.product_repo.get_by_shop(self.shop_id, limit=10)
            shop_info = self.shop_info

            # Nếu không có sản phẩm
            if not products:
                response_content = (
                    "Shop của bạn hiện chưa có sản phẩm nào hoặc chưa có dữ liệu đánh giá. "
                    "Vui lòng cập nhật sản phẩm và khuyến khích khách hàng đánh giá để nhận được tư vấn chiến lược marketing cá nhân hóa, hiệu quả nhất cho shop của bạn."
                )
                return self._create_response(response_content, {"products": []})

            # Chuẩn bị dữ liệu sản phẩm thực tế (tối đa 10 sản phẩm, truyền dạng JSON rõ ràng)
            product_data = [
                {
                    "product_id": p.product_id,
                    "name": p.name,
                    "price": p.price,
                    "quantity_sold": p.quantity_sold,
                    "rating_average": p.rating_average,
                    "review_count": p.review_count,
                    "review_text": p.review_text,
                    "short_description": p.short_description,
                }
                for p in products
            ]

            # Nếu câu hỏi có từ khóa cần search web (ví dụ: xu hướng, chính sách, đối thủ, thị trường...)
            web_results = None
            keywords = ["xu hướng", "trend", "chính sách", "luật", "đối thủ", "thị trường", "benchmark", "mới nhất", "news"]
            if any(kw in request.message.lower() for kw in keywords):
                from functions import web_search
                try:
                    web_results = web_search(
                        search_term=request.message,
                        explanation="Tìm kiếm thông tin mới nhất trên web để bổ sung vào tư vấn marketing cho shop."
                    )
                except Exception as e:
                    logger.warning(f"Web search failed: {e}")
                    web_results = None

            # Tạo prompt động cho LLM, nhấn mạnh PHẢI sử dụng dữ liệu sản phẩm
            prompt = (
                f"Shop: {getattr(shop_info, 'shop_name', None)} (ID: {self.shop_id})\n"
                "Dưới đây là dữ liệu thực tế về sản phẩm của shop (bạn PHẢI sử dụng dữ liệu này để phân tích và trả lời, không được trả lời chung chung):\n"
                f"{json.dumps(product_data, ensure_ascii=False, indent=2)}\n"
                f"Câu hỏi của shop: {request.message}\n"
            )
            if web_results and hasattr(web_results, 'results'):
                prompt += f"\nKết quả tìm kiếm web liên quan: {web_results.results}\n"
            elif web_results:
                prompt += f"\nKết quả tìm kiếm web liên quan: {web_results}\n"
            prompt += (
                "---\n"
                "YÊU CẦU: Phải phân tích, nhận xét, đề xuất dựa trên dữ liệu sản phẩm thực tế của shop. "
                "Nếu shop hỏi về marketing, hãy phân tích điểm mạnh/yếu từng sản phẩm, đề xuất chiến lược phù hợp. "
                "Nếu shop hỏi về vấn đề khác, hãy trả lời đúng trọng tâm, sử dụng dữ liệu sản phẩm nếu liên quan. "
                "Nếu có thông tin ngoài, hãy liên hệ thực tế shop và giải thích rõ ràng."
            )

            # Gọi LLM thực tế (hoặc placeholder)
            # response_content = call_gpt4o_mini(self.system_message, prompt)
            response_content = "[GPT-4o-mini trả lời ở đây dựa trên dữ liệu thực tế, câu hỏi và kết quả web nếu có]"  # Placeholder

            return self._create_response(response_content, {"products": product_data, "web_results": web_results})
        except Exception as e:
            logger.error(f"Error in MarketingAgent.process: {str(e)}")
            return self._get_error_response()

    def _get_response_title(self, query: str) -> str:
        return f"Marketing - Phân tích & Chiến lược cho Shop {self.shop_id}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi cần thêm dữ liệu sản phẩm hoặc thông tin shop để tư vấn chiến lược marketing tối ưu."

class Marketing:
    def __init__(self, db: Session, shop_id: int):
        self.db = db
        self.agent = MarketingAgent(shop_id, db)

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            shop_request = ShopRequest(**request)
            response = await self.agent.process(shop_request)
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

@router.post("/query")
async def query_marketing(request: ChatMessageRequest):
    try:
        db = Session()
        shop_id = request.sender_id if request.sender_type == "shop" else None
        if not shop_id:
            raise HTTPException(status_code=400, detail="Thiếu shop_id để phân tích chiến lược marketing cá nhân hóa.")
        marketing = Marketing(db, shop_id)
        shop_request = ShopRequest(
            message=request.content,
            chat_id=request.chat_id,
            shop_id=shop_id,
            user_id=None,
            context=request.message_metadata if request.message_metadata else {},
            entities={},
            agent_messages=[],
            filters={}
        )
        response = await marketing.process_request(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_marketing: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_marketing_campaigns():
    return {"message": "Get marketing campaigns endpoint"} 