from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.products import ProductRepositories
from repositories.search import SearchRepository
from repositories.message import MessageRepository
from models.products import ProductCreate, ProductUpdate, Product
from models.chats import ChatMessageCreate
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from env import env
from services.search import SearchServices
import traceback

router = APIRouter(prefix="/shop/products", tags=["Shop Products"])

class ProductManagementAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="ProductManagementAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và hướng dẫn cho người bán về quản lý sản phẩm.

Nhiệm vụ của bạn:
1. Hướng dẫn quản lý sản phẩm
2. Tư vấn tối ưu thông tin sản phẩm
3. Hỗ trợ xử lý các vấn đề về sản phẩm
4. Đề xuất cách tăng hiệu quả bán hàng

Các chức năng chính:
1. Thêm sản phẩm mới:
   - Tạo sản phẩm mới
   - Nhập thông tin chi tiết
   - Tải lên hình ảnh
   - Thiết lập giá và tồn kho
   - Phân loại sản phẩm

2. Cập nhật sản phẩm:
   - Sửa thông tin cơ bản
   - Cập nhật giá và tồn kho
   - Thêm/xóa hình ảnh
   - Cập nhật mô tả
   - Thay đổi trạng thái

3. Quản lý danh mục:
   - Tạo danh mục mới
   - Phân loại sản phẩm
   - Sắp xếp thứ tự
   - Quản lý thuộc tính
   - Tối ưu hiển thị

4. Tối ưu sản phẩm:
   - Tối ưu tiêu đề
   - Cải thiện mô tả
   - Tối ưu hình ảnh
   - Tăng khả năng tìm kiếm
   - Nâng cao trải nghiệm

5. Xử lý vấn đề:
   - Sản phẩm vi phạm
   - Báo cáo sai phạm
   - Khôi phục sản phẩm
   - Xử lý khiếu nại
   - Hỗ trợ khẩn cấp

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
        self.collection_name = "product_management_embeddings"
        self.agent_name = "ProductManagementAgent"

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Người bán hỏi: {query}\n"
            f"Thông tin quản lý sản phẩm liên quan:\n{context}\n"
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
        return f"Quản lý sản phẩm - {query.split()[0] if query else 'Hỗ trợ'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết về vấn đề này. Vui lòng liên hệ bộ phận hỗ trợ shop để được tư vấn cụ thể hơn."

    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        # Placeholder implementation. Replace with actual logic as needed.
        return {
            "response": {
                "title": self._get_response_title(request.message),
                "content": "Product management processing not yet implemented.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.name,
            "context": {
                "search_results": [],
                "shop_id": request.shop_id
            },
            "timestamp": datetime.now().isoformat()
        }

class ProductManagement:
    def __init__(self, db: Session):
        self.db = db
        self.agent = ProductManagementAgent()
        self.product_repository = ProductRepositories(db)

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a product management request"""
        try:
            # Lấy thông tin sản phẩm của shop
            shop_id = request.get('shop_id')
            if shop_id:
                products = await self.product_repository.get_by_shop(shop_id)
                if products:
                    product_info = "\n".join([
                        f"- {p.name} (ID: {p.product_id}): {p.price}đ - Đã bán {p.quantity_sold} sản phẩm - Đánh giá: {p.rating_average}/5 ({p.review_count} đánh giá)"
                        for p in products
                    ])
                    request['message'] = f"Danh sách sản phẩm của shop:\n{product_info}"
                else:
                    request['message'] = "Shop chưa có sản phẩm nào."
            else:
                request['message'] = "Không tìm thấy thông tin shop."

            response = await self.agent.process_request(ShopRequest(**request))
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

@router.post("/query")
async def query_product_management(request: ChatMessageRequest):
    try:
        product_management = ProductManagement(Session())
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
        response = await product_management.process_request(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_product_management: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_products():
    """List all products in a shop"""
    return {"message": "List products endpoint"} 