import json
from typing import Any, Dict, List, Optional, Union

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from env import env
from models.chats import ChatMessageCreate
from repositories.message import MessageRepository
from services.products import ProductServices
from repositories.search_compare import SearchCompareRepository
from db import SessionLocal

router = APIRouter(prefix="/product-comparison", tags=["Product Comparison"])

class ComparisonRequest(BaseModel):
    chat_id: int
    message: str
    product_ids: Optional[List[int]] = None
    entities: Optional[Dict[str, Any]] = None

class ComparisonResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    products: List[Dict[str, Any]] = Field(default_factory=list, description="Danh sách sản phẩm so sánh")
    comparison_table: Dict[str, List[Any]] = Field(default_factory=dict, description="Bảng so sánh các thuộc tính")
    comparison_summary: str = Field("", description="Tóm tắt so sánh")
    
class ProductComparisonAgent:
    def __init__(self):
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.agent = self._create_comparison_agent()
        self.db = SessionLocal()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

    def _create_comparison_agent(self) -> ConversableAgent:
        system_message = """
        Bạn là Product Comparison Agent thông minh cho hệ thống thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. So sánh các sản phẩm theo các tiêu chí khác nhau (giá, tính năng, thông số kỹ thuật)
        2. Tạo bảng so sánh trực quan
        3. Đưa ra nhận xét khách quan về ưu/nhược điểm của từng sản phẩm
        4. Giúp người dùng đưa ra quyết định mua hàng
        
        Mỗi khi nhận được yêu cầu, bạn cần xác định:
        1. Các sản phẩm cần so sánh (IDs hoặc tên)
        2. Các tiêu chí so sánh quan trọng
        3. Cách trình bày kết quả so sánh phù hợp
        
        Hãy trả về một JSON với cấu trúc:
        {
            "product_identifiers": [
                {"type": "id | name", "value": "giá trị 1"},
                {"type": "id | name", "value": "giá trị 2"}
            ],
            "comparison_criteria": ["tiêu chí 1", "tiêu chí 2", "tiêu chí 3"],
            "focus": "price | features | specifications | all"
        }
        """
        return autogen.ConversableAgent(
            name="product_comparison",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_comparison_query(self, response: str) -> Dict[str, Any]:
        try:
            # Tìm JSON trong kết quả
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning(f"Không tìm thấy JSON trong phản hồi: {response}")
                return {
                    "product_identifiers": [],
                    "comparison_criteria": ["giá", "thông số kỹ thuật", "đánh giá"],
                    "focus": "all"
                }
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi giải mã JSON: {e}")
            return {
                "product_identifiers": [],
                "comparison_criteria": ["giá", "thông số kỹ thuật", "đánh giá"],
                "focus": "all"
            }

    def _get_brand_name(self, brand_id):
        from models.brands import Brand
        brand = self.db.query(Brand).filter(Brand.brand_id == brand_id).first()
        return brand.brand_name if brand else "N/A"

    def _get_category_name(self, category_id):
        from models.categories import Category
        category = self.db.query(Category).filter(Category.category_id == category_id).first()
        return category.name if category else "N/A"

    def _find_products(self, product_identifiers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        products = []
        
        for identifier in product_identifiers:
            id_type = identifier.get("type")
            value = identifier.get("value")
            
            if id_type == "id" and isinstance(value, int):
                # Query directly by ID
                product = ProductServices(self.db).get(value)
                if product:
                    product_dict = product.__dict__.copy()
                    product_dict["brand_name"] = self._get_brand_name(product_dict.get("brand_id"))
                    product_dict["category_name"] = self._get_category_name(product_dict.get("category_id"))
                    products.append(product_dict)
            elif id_type == "name" and isinstance(value, str):
                try:
                    # First try direct database search
                    search_results = ProductServices(self.db).search(value)
                    if search_results:
                        product = search_results[0]
                        product_dict = product.__dict__.copy()
                        product_dict["brand_name"] = self._get_brand_name(product_dict.get("brand_id"))
                        product_dict["category_name"] = self._get_category_name(product_dict.get("category_id"))
                        products.append(product_dict)
                        continue

                    # If no direct match found, try semantic search
                    clean_name = value.lower().strip()
                    results = SearchCompareRepository.semantic_search(
                        query=clean_name,
                        limit=3
                    )
                    
                    if results:
                        # Try to find the best match
                        best_match = None
                        for result in results:
                            product = ProductServices(self.db).get(result["payload"]["product_id"])
                            if product:
                                if clean_name in product.name.lower():
                                    best_match = product
                                    break
                        if best_match:
                            product_dict = best_match.__dict__.copy()
                            product_dict["brand_name"] = self._get_brand_name(product_dict.get("brand_id"))
                            product_dict["category_name"] = self._get_category_name(product_dict.get("category_id"))
                            products.append(product_dict)
                        else:
                            product = ProductServices(self.db).get(results[0]["payload"]["product_id"])
                            if product:
                                product_dict = product.__dict__.copy()
                                product_dict["brand_name"] = self._get_brand_name(product_dict.get("brand_id"))
                                product_dict["category_name"] = self._get_category_name(product_dict.get("category_id"))
                                products.append(product_dict)
                except Exception as e:
                    logger.error(f"Error searching for product '{value}': {str(e)}")
                    continue
        return products

    def _extract_common_attributes(self, products: List[Dict[str, Any]]) -> List[str]:
        if not products:
            return []
        common_attributes = [
            "name", "price", "brand_name", "category_name", "rating_average", "short_description"
        ]
        spec_keys = set()
        for product in products:
            specs = product.get("specifications", {})
            if specs and isinstance(specs, dict):
                spec_keys.update(specs.keys())
        for key in spec_keys:
            if all(key in product.get("specifications", {}) for product in products):
                common_attributes.append(f"spec_{key}")
        return common_attributes

    def _create_comparison_table(self, products: List[Dict[str, Any]], criteria: List[str]) -> Dict[str, List[Any]]:
        """Tạo bảng so sánh các sản phẩm theo tiêu chí"""
        if not products:
            return {}
            
        # Xác định các thuộc tính cần so sánh
        attributes = self._extract_common_attributes(products)
        
        # Lọc thuộc tính theo tiêu chí
        filtered_attributes = []
        for attr in attributes:
            # Thuộc tính cơ bản
            if attr in ["name", "price", "brand_name", "category_name"]:
                filtered_attributes.append(attr)
                continue
                
            # Lọc theo tiêu chí
            if "giá" in criteria and attr == "price":
                filtered_attributes.append(attr)
            elif "thương hiệu" in criteria and attr == "brand_name":
                filtered_attributes.append(attr)
            elif "đánh giá" in criteria and attr == "rating_average":
                filtered_attributes.append(attr)
            elif "thông số" in criteria or "kỹ thuật" in criteria:
                if attr.startswith("spec_"):
                    filtered_attributes.append(attr)
                    
        if not filtered_attributes:
            filtered_attributes = attributes
            
        # Tạo bảng so sánh
        comparison_table = {"attributes": []}
        
        # Thêm tên thuộc tính
        for attr in filtered_attributes:
            if attr.startswith("spec_"):
                attr_name = attr[5:]  # Bỏ tiền tố "spec_"
            else:
                attr_name = attr
            comparison_table["attributes"].append(attr_name)
            
        # Thêm giá trị cho từng sản phẩm
        for i, product in enumerate(products):
            product_key = f"product_{i+1}"
            comparison_table[product_key] = []
            
            for attr in filtered_attributes:
                if attr.startswith("spec_"):
                    # Lấy từ specifications
                    spec_key = attr[5:]
                    value = product.get("specifications", {}).get(spec_key, "N/A")
                else:
                    # Lấy trực tiếp từ sản phẩm
                    value = product.get(attr, "N/A")
                    
                comparison_table[product_key].append(value)
                
        return comparison_table

    def _generate_comparison_summary(self, products: List[Dict[str, Any]], comparison_table: Dict[str, List[Any]]) -> str:
        summary = "### Tóm tắt so sánh\n\n"
        # So sánh giá
        prices = [p.get("price", 0) for p in products]
        if len(set(prices)) > 1:
            idx_max = prices.index(max(prices))
            idx_min = prices.index(min(prices))
            summary += f"- {products[idx_max]['name']} có giá cao hơn ({products[idx_max]['price']:,} VNĐ) so với {products[idx_min]['name']} ({products[idx_min]['price']:,} VNĐ).\n"
        # So sánh đánh giá
        ratings = [p.get("rating_average", 0) for p in products]
        if len(set(ratings)) > 1:
            idx_max = ratings.index(max(ratings))
            idx_min = ratings.index(min(ratings))
            summary += f"- {products[idx_max]['name']} được đánh giá cao hơn ({products[idx_max]['rating_average']}) so với {products[idx_min]['name']} ({products[idx_min]['rating_average']}).\n"
        # So sánh thương hiệu
        brands = [p.get("brand_name", "N/A") for p in products]
        if len(set(brands)) > 1:
            summary += "- Các sản phẩm thuộc các thương hiệu khác nhau: " + ", ".join(set(brands)) + ".\n"
        else:
            summary += f"- Cả hai sản phẩm đều thuộc thương hiệu {brands[0]}.\n"
        # So sánh danh mục
        categories = [p.get("category_name", "N/A") for p in products]
        if len(set(categories)) > 1:
            summary += "- Các sản phẩm thuộc các danh mục khác nhau: " + ", ".join(set(categories)) + ".\n"
        else:
            summary += f"- Cả hai sản phẩm đều thuộc danh mục {categories[0]}.\n"
        # Mô tả ngắn
        summary += "**Mô tả ngắn:**\n"
        for p in products:
            summary += f"- {p['name']}: {p.get('short_description', '')}\n"
        return summary

    def _format_comparison_response(self, products: List[Dict[str, Any]], comparison_table: Dict[str, List[Any]], comparison_summary: str) -> str:
        """Định dạng kết quả so sánh thành văn bản phản hồi"""
        if not products:
            return "Không tìm thấy sản phẩm để so sánh. Vui lòng cung cấp ID hoặc tên sản phẩm chính xác."
            
        if len(products) < 2:
            return f"Chỉ tìm thấy 1 sản phẩm ({products[0]['name']}). Cần ít nhất 2 sản phẩm để so sánh."
            
        # Tạo tiêu đề
        response = f"### So sánh {len(products)} sản phẩm\n\n"
        
        # Liệt kê sản phẩm
        response += "**Sản phẩm so sánh:**\n"
        for i, product in enumerate(products):
            response += f"{i+1}. {product['name']} - {product.get('price', 0):,} VNĐ\n"
        response += "\n"
        
        # Thêm tóm tắt so sánh
        response += comparison_summary
        
        # Thêm bảng so sánh chi tiết
        response += "\n### Bảng so sánh chi tiết\n\n"
        response += "| Thuộc tính |"
        
        # Thêm tên sản phẩm vào header
        for i in range(len(products)):
            response += f" {products[i]['name']} |"
        response += "\n"
        
        # Thêm dòng phân cách
        response += "|" + "---|" * (len(products) + 1) + "\n"
        
        # Thêm từng dòng so sánh
        attributes = comparison_table.get("attributes", [])
        for i, attr in enumerate(attributes):
            response += f"| **{attr}** |"
            
            for j in range(len(products)):
                product_key = f"product_{j+1}"
                value = comparison_table.get(product_key, [])[i]
                
                # Định dạng giá tiền
                if attr.lower() == "price" and isinstance(value, (int, float)):
                    value = f"{value:,} VNĐ"
                    
                response += f" {value} |"
            response += "\n"
            
        return response

    async def process_request(self, request: Union[ComparisonRequest, 'ChatbotRequest']) -> ComparisonResponse:
        try:
            # Convert ChatbotRequest to ComparisonRequest if needed
            if hasattr(request, 'entities'):
                product_ids = None
                if request.entities and 'product_ids' in request.entities:
                    try:
                        product_ids = request.entities['product_ids']
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid product_ids in entities: {request.entities.get('product_ids')}")
                
                request = ComparisonRequest(
                    chat_id=request.chat_id,
                    message=request.message,
                    product_ids=product_ids,
                    entities=request.entities
                )

            # Get comparison query from LLM
            response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": request.message}]
            )
            
            # Extract comparison query
            if isinstance(response, str):
                comparison_query = self._extract_comparison_query(response)
            else:
                comparison_query = self._extract_comparison_query(response.get('content', ''))
            
            # Find products to compare
            products = []
            if request.product_ids:
                # Use provided product IDs
                for product_id in request.product_ids:
                    product = ProductServices(self.db).get(product_id)
                    if product:
                        products.append(product.__dict__)
            else:
                # Use product identifiers from LLM response
                products = self._find_products(comparison_query.get('product_identifiers', []))
            
            if not products:
                return ComparisonResponse(
                    content="Xin lỗi, tôi không tìm thấy sản phẩm để so sánh. Vui lòng cung cấp tên hoặc ID sản phẩm cụ thể.",
                    products=[],
                    comparison_table={},
                    comparison_summary=""
                )
            
            # Create comparison table
            comparison_table = self._create_comparison_table(
                products,
                comparison_query.get('comparison_criteria', [])
            )
            
            # Generate comparison summary
            comparison_summary = self._generate_comparison_summary(products, comparison_table)
            
            # Format response
            content = self._format_comparison_response(products, comparison_table, comparison_summary)
            
            return ComparisonResponse(
                content=content,
                products=products,
                comparison_table=comparison_table,
                comparison_summary=comparison_summary
            )
            
        except Exception as e:
            logger.error(f"Lỗi trong product_comparison_agent: {str(e)}")
            return ComparisonResponse(
                content=f"Xin lỗi, đã xảy ra lỗi khi so sánh sản phẩm: {str(e)}",
                products=[],
                comparison_table={},
                comparison_summary=""
            )

@router.post("/compare", response_model=ComparisonResponse)
async def compare_products(request: ComparisonRequest):
    try:
        agent = ProductComparisonAgent()
        response = await agent.process_request(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong compare_products endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}") 