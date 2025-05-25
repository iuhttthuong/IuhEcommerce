from fastapi import APIRouter, HTTPException
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.message import MessageRepository
from models.chats import ChatMessageCreate
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from services.search import SearchServices
import traceback

router = APIRouter(prefix="/shop/customer-service", tags=["Shop Customer Service"])

class CustomerServiceAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="CustomerServiceAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và hướng dẫn cho người bán về dịch vụ khách hàng.

Nhiệm vụ của bạn:
1. Tư vấn quản lý khách hàng
2. Hướng dẫn xử lý khiếu nại
3. Tư vấn chăm sóc khách hàng
4. Đề xuất cải thiện dịch vụ

Các chức năng chính:
1. Quản lý khách hàng:
   - Phân tích khách hàng
   - Theo dõi tương tác
   - Đánh giá mức độ hài lòng
   - Xây dựng mối quan hệ
   - Tăng trải nghiệm

2. Xử lý khiếu nại:
   - Tiếp nhận khiếu nại
   - Phân tích nguyên nhân
   - Đề xuất giải pháp
   - Theo dõi xử lý
   - Đánh giá kết quả

3. Chăm sóc khách hàng:
   - Tư vấn sản phẩm
   - Hỗ trợ đặt hàng
   - Giải đáp thắc mắc
   - Xử lý vấn đề
   - Tăng trải nghiệm

4. Cải thiện dịch vụ:
   - Phân tích phản hồi
   - Đề xuất cải thiện
   - Tối ưu quy trình
   - Tăng hiệu quả
   - Nâng cao chất lượng

Khi trả lời, bạn cần:
- Tập trung vào lợi ích của người bán
- Cung cấp hướng dẫn chi tiết
- Đề xuất giải pháp tối ưu
- Sử dụng ngôn ngữ chuyên nghiệp
- Cung cấp ví dụ cụ thể
- Nhấn mạnh các điểm quan trọng
- Hướng dẫn từng bước khi cần"""
        )
        self.message_repository = MessageRepository()
        self.collection_name = "customer_service_embeddings"
        self.agent_name = "CustomerServiceAgent"

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Người bán hỏi: {query}\n"
            f"Thông tin dịch vụ khách hàng liên quan:\n{context}\n"
            "Hãy trả lời theo cấu trúc sau:\n"
            "1. Tóm tắt vấn đề:\n"
            "   - Mục đích và phạm vi\n"
            "   - Đối tượng áp dụng\n"
            "   - Tầm quan trọng\n\n"
            "2. Hướng dẫn chi tiết:\n"
            "   - Các bước thực hiện\n"
            "   - Yêu cầu cần thiết\n"
            "   - Lưu ý quan trọng\n\n"
            "3. Quy trình xử lý:\n"
            "   - Các bước thực hiện\n"
            "   - Thời gian xử lý\n"
            "   - Tài liệu cần thiết\n\n"
            "4. Tối ưu và cải thiện:\n"
            "   - Cách tối ưu\n"
            "   - Cải thiện hiệu quả\n"
            "   - Tăng trải nghiệm\n\n"
            "5. Khuyến nghị:\n"
            "   - Giải pháp tối ưu\n"
            "   - Cải thiện quy trình\n"
            "   - Tăng hiệu quả\n\n"
            "Trả lời cần:\n"
            "- Chuyên nghiệp và dễ hiểu\n"
            "- Tập trung vào lợi ích của người bán\n"
            "- Cung cấp hướng dẫn chi tiết\n"
            "- Đề xuất giải pháp tối ưu\n"
            "- Cung cấp ví dụ cụ thể"
        )

    def _get_response_title(self, query: str) -> str:
        return f"Dịch vụ khách hàng - {query.split()[0] if query else 'Hỗ trợ'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết về vấn đề này. Vui lòng liên hệ bộ phận hỗ trợ shop để được tư vấn cụ thể hơn."

    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        # Placeholder implementation. Replace with actual logic as needed.
        return {
            "response": {
                "title": self._get_response_title(request.message),
                "content": "Customer service processing not yet implemented.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.name,
            "context": {
                "search_results": [],
                "shop_id": request.shop_id
            },
            "timestamp": datetime.now().isoformat()
        }

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.agent = CustomerServiceAgent()

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a customer service request"""
        try:
            # Convert to ShopRequest format
            shop_request = ShopRequest(**request)
            response = await self.agent.process_request(shop_request)
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

@router.post("/query")
async def query_customer_service(request: ChatMessageRequest):
    try:
        customer_service = CustomerService(Session())
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
        response = await customer_service.process_request(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_customer_service: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_customer_service_info():
    """Get customer service information"""
    return {"message": "Get customer service info endpoint"} 