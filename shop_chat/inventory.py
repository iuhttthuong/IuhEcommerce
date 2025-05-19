from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.products import ProductRepository
from models.products import ProductUpdate
import json

router = APIRouter(prefix="/shop/inventory", tags=["Shop Inventory"])

class InventoryAgent:
    def __init__(self):
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
        self.product_repository = ProductRepository()

    async def process_request(self, request: ShopRequest):
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "check":
                return await self._check_inventory(action["data"], request.shop_id)
            elif action["type"] == "update":
                return await self._update_inventory(action["data"], request.shop_id)
            elif action["type"] == "alert":
                return await self._check_low_inventory(request.shop_id)
            elif action["type"] == "suggest":
                return await self._suggest_restock(request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in InventoryAgent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _parse_action(self, response):
        try:
            data = json.loads(response)
            return {
                "type": data.get("action", "unknown"),
                "data": data.get("data", {})
            }
        except:
            return {"type": "unknown", "data": {}}

    async def _check_inventory(self, data, shop_id):
        try:
            product_id = data.get("product_id")
            if product_id:
                # Check specific product
                product = await self.product_repository.get_by_id(product_id)
                if not product or product.shop_id != shop_id:
                    raise HTTPException(status_code=404, detail="Product not found")
                return {
                    "product_id": product_id,
                    "name": product.name,
                    "current_stock": product.stock
                }
            else:
                # Check all products
                products = await self.product_repository.get_by_shop_id(shop_id)
                return {
                    "inventory": [{
                        "product_id": p.id,
                        "name": p.name,
                        "current_stock": p.stock
                    } for p in products]
                }
        except Exception as e:
            logger.error(f"Error checking inventory: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _update_inventory(self, data, shop_id):
        try:
            product_id = data.get("product_id")
            new_stock = data.get("stock")
            
            if not product_id or new_stock is None:
                raise HTTPException(status_code=400, detail="Product ID and stock are required")
            
            # Verify product belongs to shop
            product = await self.product_repository.get_by_id(product_id)
            if not product or product.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Update stock
            update_data = ProductUpdate(stock=new_stock)
            updated_product = await self.product_repository.update(product_id, update_data)
            
            return {
                "message": "Tồn kho đã được cập nhật thành công",
                "product_id": product_id,
                "new_stock": new_stock
            }
        except Exception as e:
            logger.error(f"Error updating inventory: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _check_low_inventory(self, shop_id):
        try:
            # Get all products for shop
            products = await self.product_repository.get_by_shop_id(shop_id)
            
            # Define low stock threshold (e.g., 10 units)
            LOW_STOCK_THRESHOLD = 10
            
            # Filter products with low stock
            low_stock_products = [
                {
                    "product_id": p.id,
                    "name": p.name,
                    "current_stock": p.stock
                }
                for p in products
                if p.stock <= LOW_STOCK_THRESHOLD
            ]
            
            return {
                "low_stock_products": low_stock_products,
                "threshold": LOW_STOCK_THRESHOLD
            }
        except Exception as e:
            logger.error(f"Error checking low inventory: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _suggest_restock(self, shop_id):
        try:
            # Get all products for shop
            products = await self.product_repository.get_by_shop_id(shop_id)
            
            # Define restock thresholds and suggestions
            RESTOCK_THRESHOLD = 20
            SUGGESTED_RESTOCK = 50
            
            restock_suggestions = []
            for product in products:
                if product.stock <= RESTOCK_THRESHOLD:
                    restock_suggestions.append({
                        "product_id": product.id,
                        "name": product.name,
                        "current_stock": product.stock,
                        "suggested_restock": SUGGESTED_RESTOCK
                    })
            
            return {
                "restock_suggestions": restock_suggestions,
                "threshold": RESTOCK_THRESHOLD,
                "suggested_quantity": SUGGESTED_RESTOCK
            }
        except Exception as e:
            logger.error(f"Error suggesting restock: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.get("/")
async def get_inventory():
    """Get shop inventory"""
    return {"message": "Get inventory endpoint"} 