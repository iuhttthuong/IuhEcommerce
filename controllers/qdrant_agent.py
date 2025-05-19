import json
import re
import time
from typing import Any, Dict, List, Optional

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
from google import genai
from embedding.main import COLLECTIONS
from embedding.chatbot import retrieve_relevant_context, chat_completion_with_context
from embedding.recommendation import get_text_based_recommendations, get_similar_products
from services.chat import ChatService
from models.chat import ChatCreate
from repositories.chat import ChatRepository
from repositories.customers import CustomerRepository
from models.customers import CustomerCreate

client = genai.Client(api_key=env.GEMINI_API_KEY)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatbotRequest(BaseModel):
    chat_id: int
    message: str

class AgentResponse(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi từ agent")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Dữ liệu kết quả từ agent")
    status: str = Field(default="success", description="Trạng thái phản hồi")
    execution_time: Optional[float] = None

    class Config:
        from_attributes = True


class QdrantAgent:
    def __init__(self):
        """Initialize the QdrantAgent with necessary configurations and models."""
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.db_schema = self._get_db_schema()
        self.agent = self._create_qdrant_agent()
        
        # Define common keywords for general questions
        self.general_keywords = [
            "chính sách", "bảo hành", "đổi trả", "vận chuyển", "giao hàng",
            "thanh toán", "hoàn tiền", "khuyến mãi", "cách dùng", "hướng dẫn",
            "so sánh", "phân biệt", "là gì", "cách thức", "thủ tục"
        ]
        
        # Patterns for identifying specific product queries
        self.specific_product_patterns = [
            r"tìm.*sản phẩm",
            r"sản phẩm.*tên là",
            r"mua.*model", 
            r"tôi muốn mua",
            r"tôi đang tìm",
            r"có.*bán.*không"
        ]

    def _get_db_schema(self) -> str:
        """Return the database schema information for Qdrant collections."""
        return f"""
        QDRANT COLLECTIONS (Vector Database):

        Collection: {COLLECTIONS["products"]}
        - Các thông tin sản phẩm bao gồm: tên, mô tả, thông số, thuộc tính, v.v.
        
        Collection: {COLLECTIONS["faqs"]}
        - Câu hỏi thường gặp và câu trả lời
        
        Collection: {COLLECTIONS["reviews"]}
        - Đánh giá sản phẩm từ người dùng
        
        Collection: {COLLECTIONS["categories"]}
        - Thông tin về các danh mục sản phẩm
        
        Collection: {COLLECTIONS["chats"]}
        - Lịch sử chat với người dùng
        
        Collection: {COLLECTIONS["search_logs"]}
        - Lịch sử tìm kiếm của người dùng
        """

    def _create_qdrant_agent(self) -> ConversableAgent:
        """Create and return the Qdrant agent with system message."""
        system_message = f"""
        Bạn là một chuyên gia Qdrant (vector database) với nhiệm vụ:
        1. Phân tích câu hỏi người dùng về sản phẩm, đánh giá hoặc truy vấn semantic
        2. Xác định collection Qdrant cần truy vấn và từ khóa cần nhập vào để tìm kiếm
        3. Tạo duy nhất một JSON mô tả truy vấn Qdrant

        {self.db_schema}

        Hãy trả về mô tả truy vấn Qdrant dưới dạng JSON:

        ```json
        {{
            "collection_name": "tên collection cần truy vấn",
            "payload": "giá trị đầu vào dạng chuỗi để tìm kiếm embedding",
            "limit": 20,
            "function": "search | recommend_similar | recommend_for_user"
        }}
        ```
        """
        return autogen.ConversableAgent(
            name="qdrant_expert",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_qdrant_query(response: str):
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL) or \
                        re.search(r'(\{.*?\})', response, re.DOTALL)
        if not json_match:
            return {"collection_name": "products", "payload": "", "limit": 5}
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            return {"collection_name": "products", "payload": "", "limit": 5}
                     
        if not json_match:
            logger.warning(f"Không tìm thấy truy vấn Qdrant: {response}")
            return default_query
            
        try:
            query = json.loads(json_match.group(1))
            # Validate required fields
            if not query.get("collection_name") or not query.get("payload"):
                logger.warning("Thiếu trường bắt buộc trong JSON query")
                return {**default_query, "payload": query.get("payload", "")}
            return query
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi parse JSON: {e}")
            return default_query

    def _execute_qdrant_query(self, query_info: Dict[str, Any]) -> List[Dict]:
        """Execute query against Qdrant and return results."""
        function = query_info.get("function", "search")
        collection = query_info.get("collection_name", COLLECTIONS["products"])
        limit = query_info.get("limit", 5)
        payload = query_info.get("payload", "")

        try:
            if function == "search":
                # Kiểm tra nếu đây là yêu cầu tìm kiếm sản phẩm cụ thể
                is_specific_product_query = self._is_specific_product_query(payload)
                
                # Sử dụng chức năng tìm kiếm vector từ module embedding
                if collection == COLLECTIONS["products"]:
                    # Sử dụng ngưỡng thấp hơn cho truy vấn sản phẩm cụ thể
                    score_threshold = 0.6 if is_specific_product_query else 0.7
                    return get_text_based_recommendations(payload, limit, score_threshold)
                else:
                    # Sử dụng SearchServices với dữ liệu trực tiếp từ Qdrant
                    search_results = SearchServices.search(
                        payload=payload,
                        collection_name=collection,
                        limit=limit
                    )
                    return search_results.get("results", [])
                    
            elif function == "recommend_similar" and payload.isdigit():
                # Đề xuất sản phẩm tương tự dựa trên ID sản phẩm
                return get_similar_products(int(payload), limit)
                
            else:
                logger.debug("Chức năng không xác định, fallback về search.")
                search_results = SearchServices.search(
                    payload=payload,
                    collection_name=collection,
                    limit=limit
                )
                return search_results.get("results", [])
                
        except Exception as e:
            logger.error(f"Lỗi khi thực hiện truy vấn Qdrant: {e}")
            return []

    def _generate_explanation(self, query_info: Dict[str, Any], query_result: List[Dict], user_query: str, chat_id: int) -> str:
        """Generate human-friendly explanation from query results."""
        # Nếu không có kết quả, sử dụng RAG để trả lời
        if not query_result:
            try:
                response = chat_completion_with_context(user_query, [])
                return response.get("response", "Không tìm thấy kết quả phù hợp với yêu cầu của bạn.")
            except Exception as e:
                logger.error(f"Lỗi khi sử dụng RAG: {e}")
                return "Không tìm thấy thông tin phù hợp. Xin vui lòng thử lại với câu hỏi khác."

        # Có kết quả tìm kiếm - tạo câu trả lời
        try:
            # Chuẩn bị mô tả dữ liệu
            data_description = "Đây là một số sản phẩm mà tôi tìm thấy cho bạn: "
            
            # Xử lý dữ liệu từ các collection khác nhau
            collection_name = query_info.get("collection_name", "")
            
            if collection_name == COLLECTIONS["products"]:
                top_products = ", ".join(
                    f"{item.get('name', 'Sản phẩm không tên')} ({item.get('price', 'N/A')} VND)" 
                    for item in query_result[:3]
                )
            elif collection_name == COLLECTIONS["faqs"]:
                top_products = ", ".join(
                    f"Q: {item.get('question', 'Không có câu hỏi')} - A: {item.get('answer', 'Không có câu trả lời')}" 
                    for item in query_result[:2]
                )
            elif collection_name == COLLECTIONS["reviews"]:
                top_products = ", ".join(
                    f"Đánh giá {item.get('rating', 0)}/5: {item.get('comment', 'Không có bình luận')}" 
                    for item in query_result[:3]
                )
            else:
                # Mặc định hiển thị thông tin từ payload
                top_products = ", ".join(
                    f"ID: {item.get('id', 'N/A')}, Score: {item.get('score', 0)}" 
                    for item in query_result[:3]
                )

            data_description += f" {top_products}."

            # Tạo prompt cho Gemini để tạo câu trả lời thân thiện
            explanation_prompt = f"""
            Bạn là 1 trợ lý AI thông minh, làm việc cho một sàn thương mại điện tử IUH-Ecomerce.
            Bạn sẽ nhận đầu vào là một câu hỏi của người dùng về sản phẩm và một mô tả dữ liệu trả về từ Qdrant.
            Câu hỏi của người dùng: {user_query}
            Mô tả dữ liệu trả về: {data_description}
            Hãy viết câu trả lời thân thiện bằng tiếng Việt để giới thiệu về sản phẩm với:
            - Tóm tắt các sản phẩm liên quan
            - Giá cả, đặc điểm chính
            - Lời khuyên hữu ích (nếu phù hợp)
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=explanation_prompt,
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo câu trả lời: {e}")
            # Fallback - trả về mô tả đơn giản
            if query_result:
                products_text = ", ".join(item.get("name", "Sản phẩm không tên") for item in query_result[:3])
                return f"Tôi đã tìm thấy một số sản phẩm có thể phù hợp với yêu cầu của bạn: {products_text}."
            return "Tôi đã tìm thấy một số kết quả nhưng không thể tạo mô tả chi tiết. Vui lòng thử lại."

    async def process_query(self, user_query: str, chat_id: int) -> str:
        """Process a user query and return a response."""
        start_time = time.time()
        
        try:
            # Kiểm tra xem có phải câu hỏi chung hay không
            if self._is_general_question(user_query):
                # Sử dụng OpenAI RAG cho các câu hỏi chung
                response = chat_completion_with_context(user_query, [])
                return response.get("response", "Xin lỗi, tôi không hiểu câu hỏi của bạn.")
            
            # Đối với câu hỏi về sản phẩm, sử dụng agent để định tuyến
            prompt = f"""
            Hãy phân tích và tạo truy vấn Qdrant cho câu hỏi sau:
            "{user_query}"
            """
            
            # Gọi agent để phân tích câu hỏi
            agent_response = await self.agent.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Trích xuất thông tin truy vấn
            query_info = self._extract_qdrant_query(agent_response)
            query_info["chat_id"] = chat_id
            
            # Thực hiện truy vấn Qdrant
            results = self._execute_qdrant_query(query_info)
            
            # Tạo câu trả lời từ kết quả
            explanation = self._generate_explanation(query_info, results, user_query, chat_id)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Lỗi xử lý truy vấn: {str(e)}")
            return "Xin lỗi, đã xảy ra lỗi khi xử lý truy vấn của bạn. Vui lòng thử lại sau."
            
    def _is_general_question(self, query: str) -> bool:
        """Xác định xem câu hỏi có phải là câu hỏi chung hay không."""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.general_keywords)

    def _is_specific_product_query(self, query: str) -> bool:
        """Xác định xem truy vấn có đang tìm kiếm một sản phẩm cụ thể không."""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.specific_product_patterns)


@router.post("/chatbot", response_model=AgentResponse)
async def chatbot_endpoint(request: ChatbotRequest):
    """Endpoint for chatbot interactions."""
    start_time = time.time()
    
    try:
        qdrant_agent = QdrantAgent()
        content = await qdrant_agent.process_query(request.message, request.chat_id)
        execution_time = time.time() - start_time
        
        return AgentResponse(
            content=content,
            status="success",
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Lỗi tại endpoint chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")
