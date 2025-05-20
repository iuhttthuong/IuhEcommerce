from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, BaseShopAgent, ShopChatRequest, ShopChatResponse
from repositories.products import ProductRepositories
from models.products import ProductUpdate
import json

router = APIRouter(prefix="/shop/inventory", tags=["Shop Inventory"])

class InventoryAgent(BaseShopAgent):
    def __init__(self, shop_id: int):
        super().__init__(shop_id)
        self.agent = AssistantAgent(
            name="inventory_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về quản lý tồn kho cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Kiểm tra số lượng tồn kho hiện tại
            2. Cập nhật số lượng tồn kho
            3. Cảnh báo tồn kho thấp
            4. Gợi ý lượng cần nhập thêm
            5. Quản lý tồn kho theo SKU
            
            Bạn cần đảm bảo:
            - Cập nhật tồn kho chính xác và kịp thời
            - Cảnh báo sớm khi tồn kho thấp
            - Đề xuất lượng nhập hàng phù hợp
            - Theo dõi biến động tồn kho
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "check":
                return await self._check_inventory(action["data"])
            elif action["type"] == "update":
                return await self._update_inventory(action["data"])
            elif action["type"] == "alert":
                return await self._check_low_inventory()
            elif action["type"] == "suggest":
                return await self._suggest_restock()
            else:
                return self._create_response("Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại.")
                
        except Exception as e:
            logger.error(f"Error in InventoryAgent: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    def _parse_action(self, response):
        try:
            data = json.loads(response)
            return {
                "type": data.get("action", "unknown"),
                "data": data.get("data", {})
            }
        except:
            return {"type": "unknown", "data": {}}

    async def _check_inventory(self, data) -> ShopChatResponse:
        try:
            product_id = data.get("product_id")
            if product_id:
                # Check specific product
                product = await ProductRepositories.get_by_id(product_id)
                if not product or product.shop_id != self.shop_id:
                    return self._create_response("Không tìm thấy sản phẩm")
                return self._create_response(
                    "Thông tin tồn kho sản phẩm",
                    {
                        "product_id": product_id,
                        "name": product.name,
                        "current_stock": product.stock_quantity
                    }
                )
            else:
                # Check all products
                products = await ProductRepositories.get_by_shop_id(self.shop_id)
                return self._create_response(
                    "Danh sách tồn kho",
                    {
                        "inventory": [{
                            "product_id": p.product_id,
                            "name": p.name,
                            "current_stock": p.stock_quantity
                        } for p in products]
                    }
                )
        except Exception as e:
            logger.error(f"Error checking inventory: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi kiểm tra tồn kho. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def _update_inventory(self, data) -> ShopChatResponse:
        try:
            product_id = data.get("product_id")
            new_stock = data.get("stock")
            
            if not product_id or new_stock is None:
                return self._create_response("ID sản phẩm và số lượng tồn kho là bắt buộc")
            
            # Verify product belongs to shop
            product = await ProductRepositories.get_by_id(product_id)
            if not product or product.shop_id != self.shop_id:
                return self._create_response("Không tìm thấy sản phẩm")
            
            # Update stock
            update_data = ProductUpdate(stock_quantity=new_stock)
            updated_product = await ProductRepositories.update(product_id, update_data)
            
            return self._create_response(
                "Tồn kho đã được cập nhật thành công",
                {
                    "product_id": product_id,
                    "new_stock": new_stock
                }
            )
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi cập nhật tồn kho. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def _check_low_inventory(self) -> ShopChatResponse:
        try:
            # Get all products for shop
            products = await ProductRepositories.get_by_shop_id(self.shop_id)
            
            # Define low stock threshold (e.g., 10 units)
            LOW_STOCK_THRESHOLD = 10
            
            # Filter products with low stock
            low_stock_products = [
                {
                    "product_id": p.product_id,
                    "name": p.name,
                    "current_stock": p.stock_quantity
                }
                for p in products
                if p.stock_quantity <= LOW_STOCK_THRESHOLD
            ]
            
            return self._create_response(
                "Danh sách sản phẩm tồn kho thấp",
                {
                    "low_stock_products": low_stock_products,
                    "threshold": LOW_STOCK_THRESHOLD
                }
            )
        except Exception as e:
            logger.error(f"Error checking low inventory: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi kiểm tra tồn kho thấp. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def _suggest_restock(self) -> ShopChatResponse:
        try:
            # Get all products for shop
            products = await ProductRepositories.get_by_shop_id(self.shop_id)
            
            # Define restock thresholds and suggestions
            RESTOCK_THRESHOLD = 20
            SUGGESTED_RESTOCK = 50
            
            restock_suggestions = []
            for product in products:
                if product.stock_quantity <= RESTOCK_THRESHOLD:
                    restock_suggestions.append({
                        "product_id": product.product_id,
                        "name": product.name,
                        "current_stock": product.stock_quantity,
                        "suggested_restock": SUGGESTED_RESTOCK
                    })
            
            return self._create_response(
                "Đề xuất nhập hàng",
                {
                    "restock_suggestions": restock_suggestions,
                    "threshold": RESTOCK_THRESHOLD,
                    "suggested_quantity": SUGGESTED_RESTOCK
                }
            )
        except Exception as e:
            logger.error(f"Error suggesting restock: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi đề xuất nhập hàng. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

# Add router endpoints
@router.get("/")
async def get_inventory():
    """Get shop inventory"""
    return {"message": "Get inventory endpoint"} 