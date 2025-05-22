import json
from typing import Any, Dict, List, Optional

import autogen
from autogen import ConversableAgent
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from env import env
from models.chats import ChatMessageCreate
from repositories.message import MessageRepository
from services.products import ProductServices
from services.search import SearchServices

router = APIRouter(prefix="/search-discovery", tags=["Search & Discovery"])

class SearchRequest(BaseModel):
    chat_id: int
    user_id: Optional[int] = None
    message: str
    entities: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    products: List[Dict[str, Any]] = Field(default_factory=list, description="Danh sách sản phẩm")
    search_query: str = Field(..., description="Truy vấn tìm kiếm")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Các bộ lọc đã áp dụng")
    total_results: int = Field(0, description="Tổng số kết quả")
    
class SearchDiscoveryAgent:
    def __init__(self):
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.agent = self._create_search_agent()

    def _create_search_agent(self) -> ConversableAgent:
        system_message = """
        Bạn là Search & Discovery Agent thông minh cho hệ thống hỗ trợ thương mại điện tử IUH-Ecommerce.
        
        Nhiệm vụ của bạn:
        1. Phân tích yêu cầu tìm kiếm từ người dùng (theo từ khóa, mô tả, đặc tính)
        2. Xác định các bộ lọc cần áp dụng (khoảng giá, danh mục, thương hiệu, đánh giá, ...)
        3. Hỗ trợ duyệt danh mục sản phẩm
        4. Chuyển đổi ngôn ngữ tự nhiên sang các truy vấn tìm kiếm có cấu trúc
        
        Các loại tìm kiếm hỗ trợ:
        - Tìm theo từ khóa (keyword search)
        - Tìm theo danh mục (category browsing)
        - Tìm theo bộ lọc (filtered search)
        - Tìm theo ngữ nghĩa (semantic search)
        
        Hãy trả về một JSON với cấu trúc:
        {
            "search_type": "keyword | category | filtered | semantic",
            "query": "Từ khóa hoặc câu truy vấn chính",
            "filters": {
                "category": "Danh mục (nếu có)",
                "brand": "Thương hiệu (nếu có)",
                "price_range": {"min": 100000, "max": 5000000},
                "rating": 4.0,
                "sort_by": "price_asc | price_desc | rating | newest"
            },
            "limit": 10
        }
        """
        return autogen.ConversableAgent(
            name="search_agent",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_search_query(self, response: str) -> Dict[str, Any]:
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
                    "search_type": "keyword", 
                    "query": "", 
                    "filters": {}, 
                    "limit": 10
                }
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi giải mã JSON: {e}")
            return {
                "search_type": "keyword", 
                "query": "", 
                "filters": {}, 
                "limit": 10
            }

    def _execute_search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            # Call search service with correct parameters
            results = SearchServices.search(
                query=query,
                collection_name="product_embeddings",
                limit=5
            )
            return results
        except Exception as e:
            logger.error(f"Lỗi khi thực hiện tìm kiếm: {str(e)}")
            raise

    def _apply_filters(self, product: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        if not filters:
            return True
            
        # Lọc theo danh mục
        if "category" in filters and filters["category"] and product.get("category_name") != filters["category"]:
            return False
            
        # Lọc theo thương hiệu
        if "brand" in filters and filters["brand"] and product.get("brand") != filters["brand"]:
            return False
            
        # Lọc theo khoảng giá
        if "price_range" in filters and isinstance(filters["price_range"], dict):
            price = product.get("price", 0)
            min_price = filters["price_range"].get("min", 0)
            max_price = filters["price_range"].get("max", float('inf'))
            if price < min_price or price > max_price:
                return False
                
        # Lọc theo đánh giá
        if "rating" in filters and filters["rating"]:
            product_rating = product.get("rating", 0)
            if product_rating < filters["rating"]:
                return False
                
        return True
        
    def _sort_products(self, products: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        if not products or not sort_by:
            return products
            
        if sort_by == "price_asc":
            return sorted(products, key=lambda x: x.get("price", 0))
        elif sort_by == "price_desc":
            return sorted(products, key=lambda x: x.get("price", 0), reverse=True)
        elif sort_by == "rating":
            return sorted(products, key=lambda x: x.get("rating", 0), reverse=True)
        elif sort_by == "newest":
            return sorted(products, key=lambda x: x.get("created_at", ""), reverse=True)
            
        return products

    def _generate_response(self, products: List[Dict[str, Any]], search_info: Dict[str, Any]) -> str:
        if not products:
            return f"Không tìm thấy sản phẩm nào phù hợp với tìm kiếm '{search_info.get('query')}'."
            
        response = f"Đã tìm thấy {len(products)} sản phẩm phù hợp với tìm kiếm '{search_info.get('query')}'.\n\n"
        
        # Hiển thị 3 sản phẩm đầu tiên
        displayed_products = products[:3]
        for i, product in enumerate(displayed_products):
            response += f"{i+1}. {product.get('name')} - {product.get('price', 0):,} VNĐ"
            if product.get("rating"):
                response += f" (⭐ {product.get('rating')})"
            response += "\n"
            
        if len(products) > 3:
            response += f"\nVà {len(products) - 3} sản phẩm khác."
            
        return response

    async def process_search(self, request: SearchRequest) -> SearchResponse:
        try:
            # Extract search query and filters
            query = request.message
            filters = request.filters or {}

            # Execute search
            results = self._execute_search(query, filters)

            # Format response
            response_content = self._generate_response(results, {
                "query": query,
                "filters": filters
            })

            # Save search message
            message_payload = ChatMessageCreate(
                chat_id=request.chat_id,
                content=query,
                sender_type="search",
                sender_id=str(request.user_id or 1),
                message_metadata={
                    "type": "search",
                    "query": query,
                    "filters": filters,
                    "result_count": len(results)
                }
            )
            MessageRepository.create_message(message_payload)

            return SearchResponse(
                content=response_content,
                products=results,
                search_query=query,
                filters_applied=filters,
                total_results=len(results)
            )

        except Exception as e:
            logger.error(f"Lỗi trong search_discovery_agent: {str(e)}")
            return SearchResponse(
                content="Xin lỗi, đã có lỗi xảy ra khi tìm kiếm sản phẩm. Vui lòng thử lại sau.",
                products=[],
                search_query=request.message,
                filters_applied={},
                total_results=0
            )

@router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    try:
        agent = SearchDiscoveryAgent()
        response = await agent.process_search(request)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong search_products endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi xử lý yêu cầu: {str(e)}") 