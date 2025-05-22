from fastapi import HTTPException, APIRouter
from autogen import AssistantAgent
from loguru import logger
from .base import config_list, BaseShopAgent, ShopChatRequest, ShopChatResponse
from repositories.products import ProductRepositories
from models.products import ProductCreate, ProductUpdate
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

router = APIRouter(prefix="/shop/products", tags=["Shop Products"])

class ProductManagementAgent(BaseShopAgent):
    def __init__(self, shop_id: int, db: Session = None):
        super().__init__(shop_id)
        self.db = db
        self.product_repository = ProductRepositories(db) if db else None
        logger.info(f"Initialized ProductManagementAgent with shop_id={shop_id}, db={db is not None}")
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

    async def process(self, request: ShopChatRequest) -> ShopChatResponse:
        """
        Process product management related requests
        """
        message = request.message.lower()
        logger.info(f"Processing message: {message} with context: {request.context}")
        
        # Add new product
        if "thêm sản phẩm" in message:
            logger.info("Handling add product request")
            return await self._handle_add_product(request)
            
        # Update product
        elif "cập nhật sản phẩm" in message:
            logger.info("Handling update product request")
            return await self._handle_update_product(request)
            
        # Delete product
        elif "xóa sản phẩm" in message:
            logger.info("Handling delete product request")
            return await self._handle_delete_product(request)
            
        # List products
        elif any(keyword in message for keyword in ["sản phẩm nào", "danh sách sản phẩm", "liệt kê sản phẩm", "tôi có những sản phẩm nào"]):
            logger.info("Handling list products request")
            return await self._handle_list_products(request)
            
        # Default response
        else:
            logger.info("No specific product action detected, returning default response")
            return self._create_response(
                "Tôi có thể giúp bạn thêm, cập nhật, xóa hoặc xem danh sách sản phẩm. Vui lòng cho biết bạn muốn thực hiện thao tác nào?",
                {"available_actions": ["thêm sản phẩm", "cập nhật sản phẩm", "xóa sản phẩm", "danh sách sản phẩm"]}
            )

    async def _handle_add_product(self, request: ShopChatRequest) -> ShopChatResponse:
        return self._create_response(
            "Để thêm sản phẩm mới, vui lòng cung cấp các thông tin sau:\n"
            "1. Tên sản phẩm\n"
            "2. Mô tả\n"
            "3. Giá\n"
            "4. Số lượng\n"
            "5. Danh mục\n"
            "6. Thương hiệu"
        )

    async def _handle_update_product(self, request: ShopChatRequest) -> ShopChatResponse:
        return self._create_response(
            "Để cập nhật sản phẩm, vui lòng cung cấp:\n"
            "1. ID sản phẩm cần cập nhật\n"
            "2. Thông tin cần thay đổi"
        )

    async def _handle_delete_product(self, request: ShopChatRequest) -> ShopChatResponse:
        return self._create_response(
            "Để xóa sản phẩm, vui lòng cung cấp ID sản phẩm cần xóa"
        )

    async def _handle_list_products(self, request: ShopChatRequest) -> ShopChatResponse:
        print(f"[DEBUG] Đã vào _handle_list_products với shop_id={self.shop_id}")
        try:
            logger.info(f"Starting _handle_list_products for shop_id={self.shop_id}")
            print(f"Qdrant filter: seller_id={int(self.shop_id)}")
            # Import Qdrant client
            from qdrant_client import QdrantClient
            from qdrant_client.http import models
            from env import env
            
            # Initialize Qdrant client
            qdrant_client = QdrantClient(
                url=env.QDRANT_URL,
                api_key=env.QDRANT_API_KEY
            )
            
            # Search in product_embeddings collection
            logger.info(f"Searching products in Qdrant for seller_id={self.shop_id}")
            search_result = qdrant_client.scroll(
                collection_name="product_embeddings",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="seller_id",
                            match=models.MatchValue(value=int(self.shop_id))
                        )
                    ]
                ),
                limit=100
            )
            
            products = search_result[0]  # Get points from scroll result
            logger.info(f"Found {len(products)} products in Qdrant")
            print(f"Found {len(products)} products in Qdrant")
            
            if not products:
                logger.info("No products found in Qdrant")
                print("No products found in Qdrant")
                return self._create_response(
                    "Chưa có sản phẩm nào trong cửa hàng của bạn",
                    {"products": []}
                )
            
            # Format product list
            product_list = []
            for p in products:
                product_info = {
                    "id": p.id,
                    "name": p.payload.get("name", ""),
                    "price": p.payload.get("price", 0),
                    "stock": p.payload.get("stock_quantity", 0),
                    "category": p.payload.get("category_id", ""),
                    "description": p.payload.get("description", "")
                }
                product_list.append(product_info)
                logger.debug(f"Added product to list: {product_info}")
                print(f"Product: {product_info}")
            
            # Create response with both formatted text and structured data
            formatted_list = "\n".join([
                f"- {p['name']} (ID: {p['id']}): {p['price']}đ - Còn {p['stock']} sản phẩm"
                for p in product_list
            ])
            
            logger.info("Successfully formatted product list")
            print("Successfully formatted product list")
            return self._create_response(
                f"Danh sách sản phẩm của cửa hàng:\n{formatted_list}",
                {"products": product_list}
            )
            
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            logger.exception("Full traceback:")
            print(f"Error listing products: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi lấy danh sách sản phẩm. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def process_request(self, request: ShopChatRequest) -> ShopChatResponse:
        try:
            # Get response from agent
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Parse the response to determine the action
            action = self._parse_action(response)
            
            # Execute the appropriate action
            if action["type"] == "create":
                return await self._create_product(action["data"])
            elif action["type"] == "update":
                return await self._update_product(action["data"])
            elif action["type"] == "delete":
                return await self._delete_product(action["data"])
            elif action["type"] == "get":
                return await self._get_product(action["data"])
            else:
                return self._create_response("Tôi không hiểu yêu cầu của bạn. Vui lòng thử lại.")
                
        except Exception as e:
            logger.error(f"Error in ProductManagementAgent: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

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

    async def _create_product(self, data) -> ShopChatResponse:
        try:
            product_data = ProductCreate(
                shop_id=self.shop_id,
                name=data.get("name"),
                description=data.get("description"),
                price=data.get("price"),
                category_id=data.get("category_id"),
                stock_quantity=data.get("stock_quantity", 0),
                images=data.get("images", [])
            )
            product = await self.product_repository.create(product_data)
            return self._create_response(
                "Sản phẩm đã được tạo thành công",
                {"product": product}
            )
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi tạo sản phẩm. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def _update_product(self, data) -> ShopChatResponse:
        try:
            product_id = data.get("product_id")
            if not product_id:
                return self._create_response("ID sản phẩm là bắt buộc")
            
            # Verify product belongs to shop
            product = await self.product_repository.get_by_id(product_id)
            if not product or product.shop_id != self.shop_id:
                return self._create_response("Không tìm thấy sản phẩm")
            
            update_data = ProductUpdate(**data)
            updated_product = await self.product_repository.update(product_id, update_data)
            return self._create_response(
                "Sản phẩm đã được cập nhật thành công",
                {"product": updated_product}
            )
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi cập nhật sản phẩm. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def _delete_product(self, data) -> ShopChatResponse:
        try:
            product_id = data.get("product_id")
            if not product_id:
                return self._create_response("ID sản phẩm là bắt buộc")
            
            # Verify product belongs to shop
            product = await self.product_repository.get_by_id(product_id)
            if not product or product.shop_id != self.shop_id:
                return self._create_response("Không tìm thấy sản phẩm")
            
            await self.product_repository.delete(product_id)
            return self._create_response("Sản phẩm đã được xóa thành công")
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi xóa sản phẩm. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

    async def _get_product(self, data) -> ShopChatResponse:
        try:
            product_id = data.get("product_id")
            if product_id:
                product = await self.product_repository.get_by_id(product_id)
                if not product or product.shop_id != self.shop_id:
                    return self._create_response("Không tìm thấy sản phẩm")
                return self._create_response("Thông tin sản phẩm", {"product": product})
            else:
                # Get all products for shop
                products = await self.product_repository.get_by_shop_id(self.shop_id)
                return self._create_response("Danh sách sản phẩm", {"products": products})
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            return self._create_response(
                "Đã có lỗi xảy ra khi lấy thông tin sản phẩm. Vui lòng thử lại sau.",
                {"error": str(e)}
            )

class ProductManagement:
    def __init__(self, db: Session):
        self.db = db
        self.agent = ProductManagementAgent(shop_id=1, db=db)  # Default shop_id, should be set properly in production
        self.product_repository = ProductRepositories(db)

    async def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """Create a new product"""
        try:
            product = await self.product_repository.create(product_data)
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product information"""
        try:
            update_data = ProductUpdate(**product_data)
            product = await self.product_repository.update(product_id, update_data)
            return product
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get product details"""
        try:
            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def list_products(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all products with optional filters"""
        try:
            products = await self.product_repository.get_by_shop(self.agent.shop_id)
            if filters:
                # Apply filters
                if "category" in filters:
                    products = [p for p in products if p.category_id == filters["category"]]
                if "min_price" in filters:
                    products = [p for p in products if p.price >= filters["min_price"]]
                if "max_price" in filters:
                    products = [p for p in products if p.price <= filters["max_price"]]
            return products
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_total_products(self) -> int:
        """Get total number of products"""
        try:
            products = await self.product_repository.get_by_shop(self.agent.shop_id)
            return len(products)
        except Exception as e:
            logger.error(f"Error getting total products: {str(e)}")
            return 0

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a product management request"""
        try:
            response = await self.agent.process_request(ShopChatRequest(**request))
            return response.dict()
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

# Add router endpoints
@router.get("/")
async def list_products():
    """List all products in a shop"""
    return {"message": "List products endpoint"} 