from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from repositories.inventory import InventoryRepository
from repositories.search import SearchRepository
from repositories.message import MessageRepository
from models.inventories import Inventory, InventoryCreate
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

router = APIRouter(prefix="/shop/inventory", tags=["Shop Inventory"])

class InventoryAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="InventoryAgent",
            system_message="""Bạn là một trợ lý AI chuyên nghiệp làm việc cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn và hướng dẫn cho người bán về quản lý tồn kho.

Nhiệm vụ của bạn:
1. Hướng dẫn quản lý tồn kho
2. Tư vấn tối ưu tồn kho
3. Hỗ trợ xử lý các vấn đề về tồn kho
4. Đề xuất cách tăng hiệu quả quản lý

Các chức năng chính:
1. Kiểm tra tồn kho:
   - Xem số lượng tồn
   - Kiểm tra trạng thái
   - Theo dõi biến động
   - Cảnh báo hết hàng
   - Báo cáo tồn kho

2. Quản lý nhập hàng:
   - Tạo đơn nhập hàng
   - Theo dõi đơn nhập
   - Xác nhận nhận hàng
   - Kiểm tra chất lượng
   - Cập nhật tồn kho

3. Quản lý xuất hàng:
   - Xác nhận đơn hàng
   - Kiểm tra tồn kho
   - Cập nhật số lượng
   - Theo dõi xuất hàng
   - Báo cáo xuất hàng

4. Tối ưu tồn kho:
   - Phân tích nhu cầu
   - Dự báo tồn kho
   - Tối ưu đặt hàng
   - Giảm chi phí tồn kho
   - Tăng hiệu quả quản lý

5. Xử lý vấn đề:
   - Thất thoát hàng
   - Sai số tồn kho
   - Hàng hết hạn
   - Hàng lỗi
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
        self.collection_name = "inventory_management_embeddings"
        self.agent_name = "InventoryAgent"

    def _build_prompt(self, query: str, context: str) -> str:
        return (
            f"Người bán hỏi: {query}\n"
            f"Thông tin quản lý tồn kho liên quan:\n{context}\n"
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
        return f"Quản lý tồn kho - {query.split()[0] if query else 'Hỗ trợ'}"

    def _get_fallback_response(self) -> str:
        return "Xin lỗi, tôi không thể tìm thấy thông tin chi tiết về vấn đề này. Vui lòng liên hệ bộ phận hỗ trợ shop để được tư vấn cụ thể hơn."

    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        # Placeholder implementation. Replace with actual logic as needed.
        return {
            "response": {
                "title": self._get_response_title(request.message),
                "content": "Inventory management processing not yet implemented.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.name,
            "context": {
                "search_results": [],
                "shop_id": request.shop_id
            },
            "timestamp": datetime.now().isoformat()
        }

class Inventory:
    def __init__(self, db: Session):
        self.db = db
        self.agent = InventoryAgent()
        self.inventory_repository = InventoryRepository(db)

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an inventory management request"""
        try:
            # Lấy thông tin tồn kho của shop
            shop_id = request.get('shop_id')
            if not shop_id:
                return {
                    "message": "Không tìm thấy thông tin shop.",
                    "type": "error"
                }

            # Lấy thông tin tồn kho
            inventory = await self.inventory_repository.get_by_virtual_type(shop_id)
            if not inventory:
                return {
                    "message": "Shop chưa có sản phẩm nào trong tồn kho.",
                    "type": "text",
                    "data": {
                        "total_items": 0,
                        "inventory": []
                    }
                }

            # Format thông tin tồn kho
            inventory_info = []
            total_value = 0
            for item in inventory:
                product_info = {
                    "product_id": item.product_id,
                    "current_stock": item.current_stock,
                    "fulfillment_type": item.fulfillment_type,
                    "product_virtual_type": item.product_virtual_type
                }
                inventory_info.append(product_info)
                # Tính tổng giá trị tồn kho nếu có thông tin giá
                if hasattr(item, 'price'):
                    total_value += item.price * item.current_stock

            # Tạo response
            response = {
                "message": f"Thông tin tồn kho của shop:\n" + "\n".join([
                    f"- Sản phẩm ID {item['product_id']}: {item['current_stock']} sản phẩm"
                    for item in inventory_info
                ]),
                "type": "text",
                "data": {
                    "total_items": len(inventory_info),
                    "total_value": total_value,
                    "inventory": inventory_info
                }
            }

            # Thêm thông tin chi tiết nếu có yêu cầu cụ thể
            message = request.get('message', '').lower()
            if 'chi tiết' in message or 'detail' in message:
                response['message'] += "\n\nChi tiết tồn kho:\n" + "\n".join([
                    f"- Sản phẩm ID {item['product_id']}:\n"
                    f"  + Số lượng: {item['current_stock']}\n"
                    f"  + Loại fulfillment: {item['fulfillment_type']}\n"
                    f"  + Loại sản phẩm: {item['product_virtual_type']}"
                    for item in inventory_info
                ])

            return response

        except Exception as e:
            logger.error(f"Error processing inventory request: {str(e)}")
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
async def query_inventory(request: ChatMessageRequest):
    try:
        inventory = Inventory(Session())
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
        response = await inventory.process(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_inventory: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_inventory():
    """List all inventory items in a shop"""
    return {"message": "List inventory endpoint"} 