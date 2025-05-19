import json
from typing import Any, Dict, List, Optional, Union

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from env import env
from models.message import CreateMessagePayload
from repositories.message import MessageRepository
from services.products import ProductServices
from services.search import SearchServices

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

    def _find_products(self, product_identifiers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        products = []
        
        for identifier in product_identifiers:
            id_type = identifier.get("type")
            value = identifier.get("value")
            
            if id_type == "id" and isinstance(value, int):
                # Truy vấn trực tiếp theo ID
                product = ProductServices.get(value)
                if product:
                    products.append(product.__dict__)
            elif id_type == "name" and isinstance(value, str):
                # Tìm kiếm theo tên sản phẩm
                results = SearchServices.search(
                    payload=value,
                    collection_name="product_name_embeddings",
                    limit=1
                )
                if results:
                    product = ProductServices.get(results[0])
                    if product:
                        products.append(product.__dict__)
                        
        return products

    def _extract_common_attributes(self, products: List[Dict[str, Any]]) -> List[str]:
        """Trích xuất các thuộc tính chung giữa các sản phẩm để so sánh"""
        if not products:
            return []
            
        # Các thuộc tính cơ bản luôn so sánh
        common_attributes = ["name", "price", "brand", "category_name", "rating"]
        
        # Thêm các thuộc tính từ specifications nếu có
        spec_keys = set()
        for product in products:
            specs = product.get("specifications", {})
            if specs and isinstance(specs, dict):
                spec_keys.update(specs.keys())
                
        # Thêm các thuộc tính specifications phổ biến
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
            if attr in ["name", "price", "brand", "category_name"]:
                filtered_attributes.append(attr)
                continue
                
            # Lọc theo tiêu chí
            if "giá" in criteria and attr == "price":
                filtered_attributes.append(attr)
            elif "thương hiệu" in criteria and attr == "brand":
                filtered_attributes.append(attr)
            elif "đánh giá" in criteria and attr == "rating":
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
        """Tạo tóm tắt so sánh giữa các sản phẩm"""
        if not products or len(products) < 2:
            return "Cần ít nhất 2 sản phẩm để so sánh."
            
        # So sánh giá
        price_diff = []
        for i in range(len(products)):
            for j in range(i+1, len(products)):
                price_i = products[i].get("price", 0)
                price_j = products[j].get("price", 0)
                
                if price_i > price_j:
                    diff = price_i - price_j
                    percent = (diff / price_j) * 100
                    price_diff.append(f"{products[i]['name']} đắt hơn {products[j]['name']} {diff:,} VNĐ ({percent:.1f}%)")
                elif price_j > price_i:
                    diff = price_j - price_i
                    percent = (diff / price_i) * 100
                    price_diff.append(f"{products[j]['name']} đắt hơn {products[i]['name']} {diff:,} VNĐ ({percent:.1f}%)")
                    
        # So sánh đánh giá
        rating_diff = []
        for i in range(len(products)):
            for j in range(i+1, len(products)):
                rating_i = products[i].get("rating", 0)
                rating_j = products[j].get("rating", 0)
                
                if rating_i > rating_j:
                    diff = rating_i - rating_j
                    rating_diff.append(f"{products[i]['name']} có đánh giá cao hơn {products[j]['name']} {diff:.1f} sao")
                elif rating_j > rating_i:
                    diff = rating_j - rating_i
                    rating_diff.append(f"{products[j]['name']} có đánh giá cao hơn {products[i]['name']} {diff:.1f} sao")
                    
        # Tạo tóm tắt
        summary = "### Tóm tắt so sánh\n\n"
        
        if price_diff:
            summary += "**So sánh giá:**\n"
            for diff in price_diff[:3]:  # Giới hạn số lượng
                summary += f"- {diff}\n"
            summary += "\n"
            
        if rating_diff:
            summary += "**So sánh đánh giá:**\n"
            for diff in rating_diff[:3]:  # Giới hạn số lượng
                summary += f"- {diff}\n"
            summary += "\n"
            
        # Thêm nhận xét về một số thông số kỹ thuật nếu có
        specs_diff = []
        for i in range(len(products)):
            for j in range(i+1, len(products)):
                specs_i = products[i].get("specifications", {})
                specs_j = products[j].get("specifications", {})
                
                # So sánh các thông số chung
                common_specs = set(specs_i.keys()) & set(specs_j.keys())
                for spec in common_specs:
                    if specs_i[spec] != specs_j[spec]:
                        specs_diff.append(f"**{spec}:** {products[i]['name']} ({specs_i[spec]}) vs {products[j]['name']} ({specs_j[spec]})")
                        
        if specs_diff:
            summary += "**So sánh thông số kỹ thuật:**\n"
            for diff in specs_diff[:5]:  # Giới hạn số lượng
                summary += f"- {diff}\n"
                
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

    async def process_request(self, request: ComparisonRequest) -> ComparisonResponse:
        try:
            # Sử dụng product_ids nếu đã được cung cấp
            if request.product_ids and len(request.product_ids) >= 2:
                products = []
                for pid in request.product_ids:
                    product = ProductServices.get(pid)
                    if product:
                        products.append(product.__dict__)
                        
                if len(products) < 2:
                    return ComparisonResponse(
                        content="Cần ít nhất 2 sản phẩm hợp lệ để so sánh.",
                        products=[],
                        comparison_table={},
                        comparison_summary=""
                    )
                    
                # Sử dụng các tiêu chí mặc định
                criteria = ["giá", "thông số kỹ thuật", "đánh giá"]
                focus = "all"
                
            else:
                # Phân tích yêu cầu để xác định sản phẩm và tiêu chí
                prompt = f"""
                Hãy phân tích yêu cầu so sánh sản phẩm sau:
                "{request.message}"
                
                Các thực thể đã được xác định:
                {request.entities if request.entities else 'Không có thông tin thực thể.'}
                """
                
                # Gọi agent để phân tích
                agent_response = await self.agent.a_generate_reply(messages=[{"role": "user", "content": prompt}])
                
                # Trích xuất thông tin truy vấn
                query_info = self._extract_comparison_query(agent_response)
                
                # Tìm sản phẩm
                products = self._find_products(query_info.get("product_identifiers", []))
                
                if len(products) < 2:
                    return ComparisonResponse(
                        content="Không thể xác định đủ sản phẩm để so sánh. Vui lòng cung cấp tên hoặc ID của ít nhất 2 sản phẩm.",
                        products=products,
                        comparison_table={},
                        comparison_summary=""
                    )
                    
                criteria = query_info.get("comparison_criteria", ["giá", "thông số kỹ thuật", "đánh giá"])
                focus = query_info.get("focus", "all")
            
            # Tạo bảng so sánh
            comparison_table = self._create_comparison_table(products, criteria)
            
            # Tạo tóm tắt so sánh
            comparison_summary = self._generate_comparison_summary(products, comparison_table)
            
            # Định dạng kết quả
            response_content = self._format_comparison_response(products, comparison_table, comparison_summary)
            
            # Lưu thông tin tương tác vào message repository
            message_repository = MessageRepository()
            response_payload = CreateMessagePayload(
                chat_id=request.chat_id,
                role="assistant",
                content=response_content,
                metadata={
                    "product_count": len(products),
                    "product_ids": [p.get("id") for p in products]
                }
            )
            message_repository.create(response_payload)
            
            return ComparisonResponse(
                content=response_content,
                products=products,
                comparison_table=comparison_table,
                comparison_summary=comparison_summary
            )
            
        except Exception as e:
            logger.error(f"Lỗi trong product_comparison_agent: {e}")
            return ComparisonResponse(
                content=f"Đã xảy ra lỗi khi so sánh sản phẩm: {str(e)}",
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