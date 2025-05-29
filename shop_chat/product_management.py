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
from env import env
from services.search import SearchServices
import traceback
from repositories.inventory import InventoryRepository

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
        self.collection_name = "product_embeddings"
        self.agent_name = "ProductManagementAgent"

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a product management request."""
        try:
            shop_id = request.get('shop_id')
            message = request.get('message', '').lower().strip()
            chat_history = request.get('chat_history', '')
            intent = request.get('intent', '')
            
            if not shop_id:
                return {"message": "Không tìm thấy thông tin shop.", "type": "error"}

            # Nếu intent là product_info, trả về thông tin sản phẩm tổng quan
            if intent == "product_info":
                products = self.product_repository.get_by_shop(shop_id)
                if not products:
                    return {
                        "message": "Shop chưa có sản phẩm nào.",
                        "type": "text",
                        "total_products": 0,
                        "products": []
                    }
                return {
                    "message": f"Shop hiện có {len(products)} sản phẩm. Bạn có thể xem danh sách, thống kê, chi tiết, phân tích hiệu quả, tối ưu sản phẩm, ...",
                    "type": "text",
                    "total_products": len(products),
                    "products": [p.__dict__ for p in products]
                }

            # Xử lý sản phẩm chưa bán được hàng (đặt ngay sau khi lấy products)
            if intent == "unsold_products" or "chưa bán được" in message or "chưa có đơn" in message:
                products = self.product_repository.get_by_shop(shop_id)
                unsold = [p for p in products if getattr(p, "quantity_sold", 0) == 0]
                if not unsold:
                    return {
                        "message": "Tất cả sản phẩm của shop đều đã có đơn hàng.",
                        "type": "text",
                        "total_products": 0,
                        "products": []
                    }
                # Format danh sách sản phẩm chưa bán được
                product_info = "\n".join(
                    f"- {p.name} (ID: {getattr(p, 'product_id', 'N/A')}):\n"
                    f"  + Giá: {getattr(p, 'price', 'N/A'):,}đ\n"
                    f"  + Tồn kho: {getattr(p, 'current_stock', 'N/A')}\n"
                    f"  + Fulfillment: {getattr(p, 'fulfillment_type', 'N/A')}\n"
                    for p in unsold
                )
                return {
                    "message": f"Danh sách sản phẩm chưa bán được hàng:\n{product_info}",
                    "type": "unsold_products",
                    "total_products": len(unsold),
                    "products": [p.__dict__ for p in unsold]
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
            logger.error(f"Error in ProductManagementAgent.process: {str(e)}")
            return {
                "message": self._get_fallback_response(),
                "type": "error"
            }

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

    async def _analyze_requirements(self, message: str) -> Dict[str, bool]:
        """Phân tích câu hỏi để xác định các yêu cầu cần xử lý bằng LLM."""
        requirements = {
            'statistics': False,
            'listing': False,
            'detail': False,
            'analysis': False,
            'optimization': False,
            'add_product': False,
            'update_product': False,
            'delete_product': False,
            'search_product': False
        }

        # Tạo prompt cho LLM để phân tích câu hỏi
        prompt = f"""Bạn là một trợ lý AI chuyên phân tích yêu cầu của người dùng về quản lý sản phẩm.
Hãy phân tích câu hỏi sau và xác định các yêu cầu liên quan:

Câu hỏi: "{message}"

Các loại yêu cầu cần xác định:
1. statistics: Yêu cầu về thống kê, số liệu, tổng số, số lượng, bao gồm cả các câu hỏi về "bao nhiêu", "tổng cộng", "tổng giá trị"
2. listing: Yêu cầu về danh sách, liệt kê, hiển thị các sản phẩm, bao gồm cả các câu hỏi về "có những sản phẩm nào"
3. detail: Yêu cầu về thông tin chi tiết, mô tả, giá, tồn kho của sản phẩm, bao gồm cả các câu hỏi về "thông tin", "mô tả"
4. analysis: Yêu cầu về phân tích, báo cáo, đánh giá hiệu quả, bao gồm cả các câu hỏi về "hiệu quả", "kết quả"
5. optimization: Yêu cầu về tối ưu, cải thiện, nâng cao hiệu quả, bao gồm cả các câu hỏi về "làm sao để", "cách cải thiện"
6. add_product: Yêu cầu về thêm, tạo mới sản phẩm, bao gồm cả các câu hỏi về "thêm mới", "tạo sản phẩm"
7. update_product: Yêu cầu về cập nhật, sửa đổi thông tin sản phẩm, bao gồm cả các câu hỏi về "sửa", "thay đổi"
8. delete_product: Yêu cầu về xóa, gỡ bỏ sản phẩm, bao gồm cả các câu hỏi về "xóa bỏ", "gỡ bỏ"
9. search_product: Yêu cầu về tìm kiếm sản phẩm, bao gồm cả các câu hỏi về "tìm", "tìm kiếm"

Hãy phân tích kỹ ngữ cảnh và ý định thực sự của người dùng, không chỉ dựa vào từ khóa.
Một câu hỏi có thể chứa nhiều yêu cầu khác nhau.

Trả về JSON với các trường boolean tương ứng với mỗi loại yêu cầu được phát hiện.
Ví dụ: {{"statistics": true, "listing": false, "detail": true, ...}}

Chỉ trả về JSON, không thêm giải thích."""

        try:
            # Sử dụng assistant để phân tích
            response = await self.assistant.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Xử lý response để đảm bảo là JSON hợp lệ
            try:
                # Thử parse trực tiếp
                analysis_result = json.loads(response)
            except json.JSONDecodeError:
                # Nếu không parse được, tìm JSON trong response
                import re
                json_match = re.search(r'\{.*\}', response)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                else:
                    raise ValueError("Không tìm thấy JSON hợp lệ trong response")
            
            # Cập nhật requirements dựa trên kết quả phân tích
            for key in requirements:
                if key in analysis_result:
                    requirements[key] = bool(analysis_result[key])
            
            return requirements
            
        except Exception as e:
            logger.error(f"Error analyzing requirements with LLM: {str(e)}")
            # Trong trường hợp lỗi, trả về requirements mặc định với statistics=True
            # vì đây là yêu cầu phổ biến nhất và an toàn nhất
            requirements['statistics'] = True
            return requirements

class ProductManagement:
    def __init__(self, db: Session):
        self.db = db
        self.agent = ProductManagementAgent()
        self.product_repository = ProductRepositories(db)
        self.inventory_repository = InventoryRepository(db)

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a product management request for shop, support statistics, listing, search, and analysis."""
        try:
            shop_id = request.get('shop_id')
            message = request.get('message', '').lower().strip()
            chat_history = request.get('chat_history', '')
            
            if not shop_id:
                return {"message": "Không tìm thấy thông tin shop.", "type": "error"}

            # Danh sách các lựa chọn tương ứng với số thứ tự
            options = [
                "Xem danh sách sản phẩm",
                "Xem thống kê sản phẩm",
                "Xem chi tiết sản phẩm",
                "Phân tích hiệu quả sản phẩm",
                "Tối ưu sản phẩm",
                "Xem thống kê theo danh mục",
                "Xem doanh thu theo sản phẩm"
            ]

            # Nếu người dùng chỉ gửi số, ánh xạ sang truy vấn tương ứng
            if message.isdigit():
                idx = int(message) - 1
                if 0 <= idx < len(options):
                    # Gọi lại process với message mới là lựa chọn tương ứng
                    return await self.process({
                        **request,
                        "message": options[idx].lower()
                    })

            # Get products from repository
            products = self.product_repository.get_by_shop(shop_id)
            if not products:
                return {
                    "message": "Shop chưa có sản phẩm nào.",
                    "type": "text",
                    "total_products": 0,
                    "products": []
                }

            # Get inventory for each product
            product_ids = [p.product_id for p in products]
            inventories = [await self.inventory_repository.get_by_product_id(pid) for pid in product_ids]
            inventory_map = {inv.product_id: inv for inv in inventories if inv}
            
            # Update product information with inventory data
            for p in products:
                inv = inventory_map.get(p.product_id)
                if inv:
                    p.current_stock = inv.current_stock
                    p.fulfillment_type = inv.fulfillment_type
                    p.product_virtual_type = inv.product_virtual_type
                else:
                    p.current_stock = None
                    p.fulfillment_type = None
                    p.product_virtual_type = None

            # Analyze requirements
            requirements = await self.agent._analyze_requirements(message)
            
            # Process based on requirements
            responses = []
            
            if requirements.get('statistics'):
                stats_response = await self._handle_statistics_request(products)
                responses.append(stats_response)
            
            if requirements.get('listing'):
                list_response = await self._handle_listing_request(products)
                responses.append(list_response)
            
            if requirements.get('detail'):
                detail_response = await self._handle_detail_request(message, products)
                responses.append(detail_response)
            
            if requirements.get('analysis'):
                analysis_response = await self._handle_analysis_request(products)
                responses.append(analysis_response)
            
            if requirements.get('optimization'):
                optimization_response = await self._handle_optimization_request(products)
                responses.append(optimization_response)

            # Add new features
            if 'category' in message or 'danh mục' in message:
                category_response = await self._handle_category_request(products)
                responses.append(category_response)

            if 'doanh thu' in message or 'revenue' in message:
                revenue_response = await self._handle_revenue_request(products)
                responses.append(revenue_response)
            
            # If no specific requirements were handled, provide a general response
            if not responses:
                return {
                    "message": f"# Thông tin sản phẩm của shop\n\n"
                              f"Shop hiện có **{len(products)}** sản phẩm. Bạn có thể:\n\n"
                              f"1. Xem danh sách sản phẩm\n"
                              f"2. Xem thống kê sản phẩm\n"
                              f"3. Xem chi tiết sản phẩm\n"
                              f"4. Phân tích hiệu quả sản phẩm\n"
                              f"5. Tối ưu sản phẩm\n"
                              f"6. Xem thống kê theo danh mục\n"
                              f"7. Xem doanh thu theo sản phẩm",
                    "type": "text",
                    "total_products": len(products),
                    "products": [p.__dict__ for p in products]
                }

            # Combine responses
            combined_message = "\n\n".join([r.get('message', '') for r in responses])
            return {
                "message": combined_message,
                "type": "text",
                "total_products": len(products),
                "products": [p.__dict__ for p in products]
            }

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

    async def _handle_count_and_category_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle request for product count and categories."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào.", "type": "count_and_category", "total_products": 0, "categories": []}

        # Calculate total products and gather categories
        categories = set(getattr(p, 'category', 'Uncategorized') for p in products)
        category_stats = {}
        for category in categories:
            category_products = [p for p in products if getattr(p, 'category', 'Uncategorized') == category]
            category_stats[category] = {
                "count": len(category_products),
                "total_value": sum(getattr(p, 'price', 0) * getattr(p, 'current_stock', 0) for p in category_products)
            }

        return {
            "message": f"Shop hiện có {len(products)} sản phẩm thuộc các danh mục: {', '.join(categories)}.",
            "type": "count_and_category",
            "total_products": len(products),
            "categories": list(categories),
            "category_stats": category_stats
        }

    async def _handle_statistics_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle statistics request with enhanced metrics."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào.", "type": "statistic", "total_products": 0}

        total_value = sum(getattr(p, 'price', 0) * getattr(p, 'current_stock', 0) for p in products)
        total_sold = sum(getattr(p, 'quantity_sold', 0) for p in products)
        avg_rating = sum(getattr(p, 'rating_average', 0) for p in products) / len(products) if products else 0
        total_reviews = sum(getattr(p, 'review_count', 0) for p in products)

        return {
            "message": f"Thống kê sản phẩm của shop:\n"
                      f"- Tổng số sản phẩm: {len(products)}\n"
                      f"- Tổng giá trị tồn kho: {total_value:,}đ\n"
                      f"- Tổng số sản phẩm đã bán: {total_sold}\n"
                      f"- Đánh giá trung bình: {avg_rating:.1f}/5\n"
                      f"- Tổng số đánh giá: {total_reviews}",
            "type": "statistic",
            "total_products": len(products),
            "total_value": total_value,
            "total_sold": total_sold,
            "avg_rating": avg_rating,
            "total_reviews": total_reviews
        }

    async def _handle_listing_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle listing request with enhanced product information."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào.", "type": "list", "products": []}

        # Sort products by different criteria based on message content
        sorted_products = sorted(products, key=lambda x: getattr(x, 'quantity_sold', 0), reverse=True)
        
        product_info = "\n".join(
            f"- {p.name} (ID: {getattr(p, 'product_id', 'N/A')}):\n"
            f"  + Giá: {getattr(p, 'price', 'N/A'):,}đ\n"
            f"  + Tồn kho: {getattr(p, 'current_stock', 'N/A')}\n"
            f"  + Fulfillment: {getattr(p, 'fulfillment_type', 'N/A')}\n"
            f"  + Đã bán: {getattr(p, 'quantity_sold', 0)}\n"
            f"  + Đánh giá: {getattr(p, 'rating_average', 0)}/5 ({getattr(p, 'review_count', 0)} đánh giá)\n"
            for p in sorted_products
        )
        
        return {
            "message": f"Danh sách sản phẩm của shop (sắp xếp theo số lượng bán):\n{product_info}",
            "type": "list",
            "products": [p.__dict__ for p in sorted_products]
        }

    async def _handle_detail_request(self, message: str, products: List[Product]) -> Dict[str, Any]:
        """Handle detail request with enhanced product information."""
        import re
        match = re.search(r'id\s*:?\s*(\d+)', message)
        product = None
        if match:
            pid = int(match.group(1))
            product = next((p for p in products if getattr(p, 'product_id', None) == pid), None)
        else:
            for p in products:
                if p.name.lower() in message:
                    product = p
                    break

        if product:
            return {
                "message": f"Thông tin chi tiết sản phẩm:\n"
                          f"- Tên: {product.name}\n"
                          f"- ID: {getattr(product, 'product_id', 'N/A')}\n"
                          f"- Giá: {getattr(product, 'price', 'N/A'):,}đ\n"
                          f"- Tồn kho: {getattr(product, 'current_stock', 'N/A')}\n"
                          f"- Fulfillment: {getattr(product, 'fulfillment_type', 'N/A')}\n"
                          f"- Đã bán: {getattr(product, 'quantity_sold', 0)}\n"
                          f"- Đánh giá: {getattr(product, 'rating_average', 0)}/5 ({getattr(product, 'review_count', 0)} đánh giá)\n"
                          f"- Mô tả: {getattr(product, 'description', 'Chưa có mô tả')}",
                "type": "detail",
                "product": product.__dict__
            }
        else:
            return {"message": "Không tìm thấy sản phẩm theo yêu cầu.", "type": "detail"}

    async def _handle_analysis_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle product analysis request."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào để phân tích.", "type": "analysis"}

        # Calculate various metrics
        total_products = len(products)
        total_value = sum(getattr(p, 'price', 0) * getattr(p, 'current_stock', 0) for p in products)
        total_sold = sum(getattr(p, 'quantity_sold', 0) for p in products)
        avg_rating = sum(getattr(p, 'rating_average', 0) for p in products) / total_products
        total_reviews = sum(getattr(p, 'review_count', 0) for p in products)

        # Find best and worst performing products
        best_selling = max(products, key=lambda x: getattr(x, 'quantity_sold', 0))
        worst_selling = min(products, key=lambda x: getattr(x, 'quantity_sold', 0))
        best_rated = max(products, key=lambda x: getattr(x, 'rating_average', 0))
        worst_rated = min(products, key=lambda x: getattr(x, 'rating_average', 0))

        return {
            "message": f"Phân tích sản phẩm của shop:\n\n"
                      f"1. Tổng quan:\n"
                      f"- Tổng số sản phẩm: {total_products}\n"
                      f"- Tổng giá trị tồn kho: {total_value:,}đ\n"
                      f"- Tổng số sản phẩm đã bán: {total_sold}\n"
                      f"- Đánh giá trung bình: {avg_rating:.1f}/5\n"
                      f"- Tổng số đánh giá: {total_reviews}\n\n"
                      f"2. Sản phẩm bán chạy nhất:\n"
                      f"- Tên: {best_selling.name}\n"
                      f"- Đã bán: {getattr(best_selling, 'quantity_sold', 0)}\n"
                      f"- Giá: {getattr(best_selling, 'price', 'N/A'):,}đ\n\n"
                      f"3. Sản phẩm bán chậm nhất:\n"
                      f"- Tên: {worst_selling.name}\n"
                      f"- Đã bán: {getattr(worst_selling, 'quantity_sold', 0)}\n"
                      f"- Giá: {getattr(worst_selling, 'price', 'N/A'):,}đ\n\n"
                      f"4. Sản phẩm được đánh giá cao nhất:\n"
                      f"- Tên: {best_rated.name}\n"
                      f"- Đánh giá: {getattr(best_rated, 'rating_average', 0)}/5\n"
                      f"- Số đánh giá: {getattr(best_rated, 'review_count', 0)}",
            "type": "analysis",
            "metrics": {
                "total_products": total_products,
                "total_value": total_value,
                "total_sold": total_sold,
                "avg_rating": avg_rating,
                "total_reviews": total_reviews
            }
        }

    async def _handle_optimization_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle product optimization request."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào để tối ưu.", "type": "optimization"}

        # Analyze products for optimization opportunities
        low_stock = [p for p in products if getattr(p, 'current_stock', 0) < 10]
        high_price = [p for p in products if getattr(p, 'price', 0) > 1000000]
        low_rated = [p for p in products if getattr(p, 'rating_average', 0) < 3]
        no_reviews = [p for p in products if getattr(p, 'review_count', 0) == 0]

        return {
            "message": f"Đề xuất tối ưu sản phẩm:\n\n"
                      f"1. Sản phẩm sắp hết hàng ({len(low_stock)}):\n"
                      f"{', '.join(p.name for p in low_stock[:5])}\n\n"
                      f"2. Sản phẩm có giá cao ({len(high_price)}):\n"
                      f"{', '.join(p.name for p in high_price[:5])}\n\n"
                      f"3. Sản phẩm có đánh giá thấp ({len(low_rated)}):\n"
                      f"{', '.join(p.name for p in low_rated[:5])}\n\n"
                      f"4. Sản phẩm chưa có đánh giá ({len(no_reviews)}):\n"
                      f"{', '.join(p.name for p in no_reviews[:5])}\n\n"
                      f"Đề xuất:\n"
                      f"- Kiểm tra và bổ sung hàng cho các sản phẩm sắp hết\n"
                      f"- Xem xét điều chỉnh giá cho các sản phẩm có giá cao\n"
                      f"- Cải thiện chất lượng và dịch vụ cho các sản phẩm có đánh giá thấp\n"
                      f"- Khuyến khích khách hàng đánh giá cho các sản phẩm chưa có đánh giá",
            "type": "optimization",
            "optimization_metrics": {
                "low_stock": len(low_stock),
                "high_price": len(high_price),
                "low_rated": len(low_rated),
                "no_reviews": len(no_reviews)
            }
        }

    async def _handle_add_product(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Giả sử request có đủ thông tin cho ProductCreate
        try:
            product_data = request.get('product_data')
            if not product_data:
                return {"message": "Thiếu thông tin sản phẩm để thêm mới.", "type": "add_product_error"}
            product = self.product_repository.create(ProductCreate(**product_data))
            return {"message": "Thêm sản phẩm thành công!", "type": "add_product", "product": product.__dict__}
        except Exception as e:
            return {"message": f"Lỗi khi thêm sản phẩm: {str(e)}", "type": "add_product_error"}

    async def _handle_update_product(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            product_id = request.get('product_id')
            update_data = request.get('update_data')
            if not product_id or not update_data:
                return {"message": "Thiếu thông tin cập nhật sản phẩm.", "type": "update_product_error"}
            product = self.product_repository.update(product_id, ProductUpdate(**update_data))
            return {"message": "Cập nhật sản phẩm thành công!", "type": "update_product", "product": product.__dict__}
        except Exception as e:
            return {"message": f"Lỗi khi cập nhật sản phẩm: {str(e)}", "type": "update_product_error"}

    async def _handle_delete_product(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            product_id = request.get('product_id')
            if not product_id:
                return {"message": "Thiếu product_id để xóa sản phẩm.", "type": "delete_product_error"}
            self.product_repository.delete(product_id)
            return {"message": "Xóa sản phẩm thành công!", "type": "delete_product"}
        except Exception as e:
            return {"message": f"Lỗi khi xóa sản phẩm: {str(e)}", "type": "delete_product_error"}

    async def _handle_search_product(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            keyword = request.get('keyword', '').lower()
            if not keyword:
                return {"message": "Thiếu từ khóa tìm kiếm.", "type": "search_product_error"}
            products = self.product_repository.search_by_keyword(keyword)
            # Lấy inventory cho từng sản phẩm tìm được
            product_ids = [p.product_id for p in products]
            inventories = [await self.inventory_repository.get_by_product_id(pid) for pid in product_ids]
            inventory_map = {inv.product_id: inv for inv in inventories if inv}
            for p in products:
                inv = inventory_map.get(p.product_id)
                if inv:
                    p.current_stock = inv.current_stock
                    p.fulfillment_type = inv.fulfillment_type
                    p.product_virtual_type = inv.product_virtual_type
                else:
                    p.current_stock = None
                    p.fulfillment_type = None
                    p.product_virtual_type = None
            return {
                "message": f"Kết quả tìm kiếm sản phẩm cho từ khóa '{keyword}': {len(products)} sản phẩm.",
                "type": "search_product",
                "products": [p.__dict__ for p in products]
            }
        except Exception as e:
            return {"message": f"Lỗi khi tìm kiếm sản phẩm: {str(e)}", "type": "search_product_error"}

    async def _handle_category_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle category statistics request."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào.", "type": "category"}

        # Group products by category
        categories = {}
        for p in products:
            category = getattr(p, 'category', 'Uncategorized')
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_value': 0,
                    'total_sold': 0,
                    'products': []
                }
            categories[category]['count'] += 1
            categories[category]['total_value'] += getattr(p, 'price', 0) * getattr(p, 'current_stock', 0)
            categories[category]['total_sold'] += getattr(p, 'quantity_sold', 0)
            categories[category]['products'].append(p)

        # Format response
        category_info = []
        for category, stats in categories.items():
            category_info.append(
                f"## {category}\n"
                f"- Số lượng sản phẩm: **{stats['count']}**\n"
                f"- Tổng giá trị tồn kho: **{stats['total_value']:,}đ**\n"
                f"- Tổng số đã bán: **{stats['total_sold']}**\n"
                f"- Top 3 sản phẩm bán chạy:\n"
                f"{self._format_top_products(stats['products'])}"
            )

        return {
            "message": f"# Thống kê theo danh mục\n\n" + "\n\n".join(category_info),
            "type": "category",
            "categories": categories
        }

    async def _handle_revenue_request(self, products: List[Product]) -> Dict[str, Any]:
        """Handle revenue statistics request."""
        if not products:
            return {"message": "Shop chưa có sản phẩm nào.", "type": "revenue"}

        # Calculate revenue for each product
        product_revenue = []
        for p in products:
            revenue = getattr(p, 'price', 0) * getattr(p, 'quantity_sold', 0)
            product_revenue.append({
                'product': p,
                'revenue': revenue
            })

        # Sort by revenue
        product_revenue.sort(key=lambda x: x['revenue'], reverse=True)

        # Format response
        revenue_info = []
        total_revenue = sum(item['revenue'] for item in product_revenue)
        
        revenue_info.append(f"# Thống kê doanh thu\n\n")
        revenue_info.append(f"## Tổng quan\n")
        revenue_info.append(f"- Tổng doanh thu: **{total_revenue:,}đ**\n")
        revenue_info.append(f"- Số sản phẩm đã bán: **{len(products)}**\n")
        revenue_info.append(f"- Doanh thu trung bình/sản phẩm: **{total_revenue/len(products):,.0f}đ**\n\n")
        
        revenue_info.append(f"## Top 5 sản phẩm doanh thu cao nhất\n")
        for i, item in enumerate(product_revenue[:5], 1):
            p = item['product']
            revenue_info.append(
                f"{i}. **{p.name}**\n"
                f"   - Doanh thu: **{item['revenue']:,}đ**\n"
                f"   - Đã bán: **{getattr(p, 'quantity_sold', 0)}**\n"
                f"   - Giá: **{getattr(p, 'price', 0):,}đ**\n"
            )

        return {
            "message": "\n".join(revenue_info),
            "type": "revenue",
            "total_revenue": total_revenue,
            "product_revenue": product_revenue
        }

    def _format_top_products(self, products: List[Product], limit: int = 3) -> str:
        """Format top products for display."""
        sorted_products = sorted(products, key=lambda x: getattr(x, 'quantity_sold', 0), reverse=True)
        result = []
        for i, p in enumerate(sorted_products[:limit], 1):
            result.append(
                f"  {i}. {p.name}\n"
                f"     - Đã bán: {getattr(p, 'quantity_sold', 0)}\n"
                f"     - Giá: {getattr(p, 'price', 0):,}đ"
            )
        return "\n".join(result)

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
        response = await product_management.process(shop_request.dict())
        return response
    except Exception as e:
        logger.error(f"Error in query_product_management: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_products():
    """List all products in a shop"""
    return {"message": "List products endpoint"}