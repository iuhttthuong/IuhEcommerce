from fastapi import APIRouter, HTTPException
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.message import MessageRepository
from repositories.customers import CustomerRepository
from models.customers import Customer, CustomerModel
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

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a customer service request."""
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
            logger.error(f"Error in CustomerServiceAgent.process: {str(e)}")
            return {
                "message": self._get_fallback_response(),
                "type": "error"
            }

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

class CustomerService:
    def __init__(self, db: Session, shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.agent = CustomerServiceAgent(shop_id)
        self.customer_repository = CustomerRepository()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a customer service request."""
        try:
            shop_id = request.get('shop_id') or self.shop_id
            message = request.get('message', '').lower()
            chat_history = request.get('chat_history', '')
            
            if not shop_id:
                return {"message": "Không tìm thấy thông tin shop.", "type": "error"}

            # Lấy thông tin khách hàng của shop
            customers = self.customer_repository.get_by_shop(shop_id)
            if not customers:
                return {
                    "message": "Shop chưa có khách hàng nào.",
                    "type": "text",
                    "data": {
                        "total_customers": 0,
                        "customers": []
                    }
                }

            # Format thông tin khách hàng
            customers_info = []
            for customer in customers:
                customer_info = {
                    "customer_id": customer.customer_id,
                    "name": f"{customer.customer_fname} {customer.customer_lname}",
                    "email": customer.customer_mail,
                    "phone": customer.customer_phone,
                    "address": customer.customer_address,
                    "dob": customer.customer_dob.isoformat() if customer.customer_dob else None,
                    "gender": customer.customer_gender
                }
                customers_info.append(customer_info)

            # Tạo response
            response = {
                "message": f"Thông tin khách hàng của shop:\n" + "\n".join([
                    f"- Khách hàng: {customer['name']}\n"
                    f"  + Email: {customer['email']}\n"
                    f"  + Số điện thoại: {customer['phone']}\n"
                    f"  + Địa chỉ: {customer['address']}"
                    for customer in customers_info
                ]),
                "type": "text",
                "data": {
                    "total_customers": len(customers_info),
                    "customers": customers_info
                }
            }

            # Thêm thông tin chi tiết nếu có yêu cầu cụ thể
            if 'chi tiết' in message or 'detail' in message:
                response['message'] += "\n\nChi tiết khách hàng:\n" + "\n".join([
                    f"- Khách hàng: {customer['name']}\n"
                    f"  + ID: {customer['customer_id']}\n"
                    f"  + Email: {customer['email']}\n"
                    f"  + Số điện thoại: {customer['phone']}\n"
                    f"  + Địa chỉ: {customer['address']}\n"
                    f"  + Ngày sinh: {customer['dob']}\n"
                    f"  + Giới tính: {customer['gender']}"
                    for customer in customers_info
                ])

            return response

        except Exception as e:
            logger.error(f"Error processing customer service request: {str(e)}")
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
        response = await customer_service.process(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_customer_service: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_customers():
    """List all customers in a shop"""
    return {"message": "List customers endpoint"} 