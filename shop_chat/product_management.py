from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, ShopRequest
from repositories.products import ProductRepository
from models.products import ProductCreate, ProductUpdate
import json

router = APIRouter(prefix="/shop/products", tags=["Shop Products"])

class ProductManagementAgent:
    def __init__(self):
        self.agent = AssistantAgent(
            name="product_management_agent",
            system_message="""Bạn là một trợ lý AI chuyên về quản lý sản phẩm cho shop trên sàn thương mại điện tử IUH-Ecomerce.
            Nhiệm vụ của bạn là:
            1. Hỗ trợ đăng sản phẩm mới
            2. Cập nhật thông tin sản phẩm
            3. Xóa sản phẩm
            4. Kiểm tra trạng thái sản phẩm
            5. Quản lý danh mục sản phẩm
            
            Bạn cần đảm bảo:
            - Thông tin sản phẩm đầy đủ và chính xác
            - Tuân thủ quy định về đăng sản phẩm của sàn
            - Tối ưu hóa mô tả và hình ảnh sản phẩm
            - Phân loại sản phẩm đúng danh mục
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
            if action["type"] == "create":
                return await self._create_product(action["data"], request.shop_id)
            elif action["type"] == "update":
                return await self._update_product(action["data"], request.shop_id)
            elif action["type"] == "delete":
                return await self._delete_product(action["data"], request.shop_id)
            elif action["type"] == "get":
                return await self._get_product(action["data"], request.shop_id)
            else:
                return {"message": "Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại."}
                
        except Exception as e:
            logger.error(f"Error in ProductManagementAgent: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _parse_action(self, response):
        # Parse the agent's response to determine the action type and data
        # This is a simplified version - you would need to implement proper parsing
        try:
            # Assuming response is in JSON format
            data = json.loads(response)
            return {
                "type": data.get("action", "unknown"),
                "data": data.get("data", {})
            }
        except:
            return {"type": "unknown", "data": {}}

    async def _create_product(self, data, shop_id):
        try:
            product_data = ProductCreate(
                shop_id=shop_id,
                name=data.get("name"),
                description=data.get("description"),
                price=data.get("price"),
                category_id=data.get("category_id"),
                stock=data.get("stock", 0),
                images=data.get("images", [])
            )
            product = await self.product_repository.create(product_data)
            return {"message": "Sản phẩm đã được tạo thành công", "product": product}
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _update_product(self, data, shop_id):
        try:
            product_id = data.get("product_id")
            if not product_id:
                raise HTTPException(status_code=400, detail="Product ID is required")
            
            # Verify product belongs to shop
            product = await self.product_repository.get_by_id(product_id)
            if not product or product.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Product not found")
            
            update_data = ProductUpdate(**data)
            updated_product = await self.product_repository.update(product_id, update_data)
            return {"message": "Sản phẩm đã được cập nhật thành công", "product": updated_product}
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _delete_product(self, data, shop_id):
        try:
            product_id = data.get("product_id")
            if not product_id:
                raise HTTPException(status_code=400, detail="Product ID is required")
            
            # Verify product belongs to shop
            product = await self.product_repository.get_by_id(product_id)
            if not product or product.shop_id != shop_id:
                raise HTTPException(status_code=404, detail="Product not found")
            
            await self.product_repository.delete(product_id)
            return {"message": "Sản phẩm đã được xóa thành công"}
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_product(self, data, shop_id):
        try:
            product_id = data.get("product_id")
            if product_id:
                product = await self.product_repository.get_by_id(product_id)
                if not product or product.shop_id != shop_id:
                    raise HTTPException(status_code=404, detail="Product not found")
                return {"product": product}
            else:
                # Get all products for shop
                products = await self.product_repository.get_by_shop_id(shop_id)
                return {"products": products}
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Add router endpoints
@router.get("/")
async def list_products():
    """List all products in a shop"""
    return {"message": "List products endpoint"} 