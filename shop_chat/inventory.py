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
    def __init__(self, db: Session, shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.agent = InventoryAgent(shop_id)
        self.inventory_repository = InventoryRepository(db)

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an inventory request."""
        try:
            shop_id = request.get('shop_id') or self.shop_id
            message = request.get('message', '').lower()
            chat_history = request.get('chat_history', '')
            
            if not shop_id:
                return {"message": "Không tìm thấy thông tin shop.", "type": "error"}

            # Lấy thông tin tồn kho
            inventory = await self.inventory_repository.get_by_product_id(str(shop_id))
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
            inventory_items = [inventory] if not isinstance(inventory, list) else inventory
            
            # Sắp xếp sản phẩm theo số lượng tồn kho
            sorted_items = sorted(inventory_items, key=lambda x: x.current_stock, reverse=True)
            highest_stock = sorted_items[:5]  # Top 5 sản phẩm tồn kho nhiều nhất
            lowest_stock = sorted_items[-5:]  # Top 5 sản phẩm tồn kho ít nhất
            
            for item in inventory_items:
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

            # Tạo prompt cho LLM
            prompt = f"""Bạn là một chuyên gia tư vấn quản lý tồn kho chuyên nghiệp.
Hãy phân tích và đề xuất chiến lược quản lý tồn kho dựa trên dữ liệu thực tế.

Yêu cầu của người bán: "{message}"

Dữ liệu tồn kho của shop:
1. Tổng quan:
   - Tổng số sản phẩm: {len(inventory_info)}
   - Tổng giá trị tồn kho: {total_value:,}đ

2. Sản phẩm tồn kho nhiều nhất:
{chr(10).join([f"- {item.product_id}: {item.current_stock} đơn vị" for item in highest_stock])}

3. Sản phẩm tồn kho ít nhất:
{chr(10).join([f"- {item.product_id}: {item.current_stock} đơn vị" for item in lowest_stock])}

Hãy phân tích và đề xuất theo cấu trúc sau:

1. 📊 **Phân tích tình hình**:
   - Đánh giá tổng quan về tồn kho
   - Phân tích sản phẩm tồn kho nhiều/ít
   - Xác định vấn đề cần giải quyết
   - Đánh giá rủi ro tồn kho

2. 🎯 **Chiến lược quản lý**:
   - Đề xuất chiến lược cho từng nhóm sản phẩm
   - Kế hoạch cân bằng tồn kho
   - Cách thức tối ưu tồn kho
   - Chiến lược đặt hàng

3. 📈 **Kế hoạch thực hiện**:
   - Các bước thực hiện cụ thể
   - Thời gian và lộ trình
   - Nguồn lực cần thiết
   - Chỉ số đánh giá hiệu quả

4. 💡 **Đề xuất sáng tạo**:
   - Ý tưởng tối ưu tồn kho
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
- Tập trung vào giải pháp tối ưu
- Đề xuất giải pháp khả thi và sáng tạo
- Cung cấp ví dụ cụ thể
- Sử dụng emoji phù hợp
- Định dạng markdown rõ ràng
- Tập trung vào lợi ích của người bán"""

            # Tạo response sử dụng assistant
            response = await self.agent.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "message": response if response else "Xin lỗi, tôi không thể tạo phản hồi phù hợp. Vui lòng thử lại sau.",
                "type": "text",
                "data": {
                    "total_items": len(inventory_info),
                    "total_value": total_value,
                    "inventory": inventory_info,
                    "highest_stock": [{"product_id": item.product_id, "current_stock": item.current_stock} for item in highest_stock],
                    "lowest_stock": [{"product_id": item.product_id, "current_stock": item.current_stock} for item in lowest_stock]
                }
            }

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