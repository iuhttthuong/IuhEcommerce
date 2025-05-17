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
        self.llm_config = {
            "model": "gpt-4o-mini",
            "api_key": env.OPENAI_API_KEY
        }
        self.db_schema = self._get_db_schema()
        self.agent = self._create_qdrant_agent()

    def _get_db_schema(self) -> str:
        return """
        QDRANT COLLECTIONS (Vector Database):

        Collection: product_name_embeddings
        point = PointStruct(
            id=product_id,
            vector={"default": embedding},
            payload={
                "product_id": product_id,
                "name": product.name,
                "description": product.description,
            }
        )

        Collection: product_des_embeddings
        point = PointStruct(
            id=product_id,
            vector={"default": embedding},
            payload={
                "product_id": product_id,
                "name": product.name,
                "description": product.description,
            }
        )
        """

    def _create_qdrant_agent(self) -> ConversableAgent:
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
            "function": "search"
        }}
        ```
        """
        return autogen.ConversableAgent(
            name="qdrant_expert",
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )

    def _extract_qdrant_query(self, response: str) -> Dict[str, Any]:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL) or \
                     re.search(r'(\{.*?\})', response, re.DOTALL)
        if not json_match:
            logger.warning(f"Không tìm thấy truy vấn Qdrant: {response}")
            return {"collection_name": "products", "payload": "", "limit": 5}
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi parse JSON: {e}")
            return {"collection_name": "products", "payload": "", "limit": 5}

    def _execute_qdrant_query(self, query_info: Dict[str, Any]) -> List[Dict]:
        function = query_info.get("function")
        collection = query_info.get("collection_name")

        if function in ("search", "recommend_for_user"):
            collection = collection if function == "search" else "user_queries"
            return SearchServices.search(
                payload=query_info.get("payload", ""),
                collection_name=collection,
                limit=query_info.get("limit")
            )

        logger.debug("Chức năng không xác định, fallback về search.")
        return SearchServices.search(
            payload=query_info.get("payload", ""),
            collection_name=collection,
            limit=query_info.get("limit")
        )

    def _generate_explanation(self, query_info: Dict[str, Any], query_result: List[Dict], user_query: str, chat_id: int) -> Dict[str, str]:
        if not query_result:
            return {"response": "Không tìm thấy kết quả phù hợp với yêu cầu của bạn."}

        data_description = f"Đây là một số sản phẩm mà tôi tìm thấy cho bạn: "
        top_products = ", ".join(
            f"{item.__dict__['name']} ({item.__dict__.get('price', 'N/A')} VND) {item.__dict__.get('product_short_url', 'N/A')}" for item in query_result[:3]
        )
        data_description += f" {top_products}."

        explanation_prompt = f"""
        Bạn là 1 trợ lý AI thông minh, làm việc cho một sàn thương mại điện tử IUH-Ecomerce.
        Bạn sẽ nhận đầu vào là một câu hỏi của người dùng về sản phẩm và một mô tả dữ liệu trả về từ Qdrant.
        Câu hỏi của người dùng: {user_query}
        Mô tả dữ liệu trả về: {data_description}
        Hãy viết câu trả lời thân thiện bằng tiếng Việt để giới thiệu về sản phẩm.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents=explanation_prompt,
        )
        return response.text



    async def process_query(self, user_query: str, chat_id: int) -> AgentResponse:
        start_time = time.time()
        try:
            prompt = f"""
            Hãy phân tích và tạo truy vấn Qdrant cho câu hỏi sau:
            "{user_query}"
            """
            print(f"Prompt: {prompt}")
            agent_response = await self.agent.a_generate_reply(messages=[{"role": "user", "content": prompt}])
            query_info = self._extract_qdrant_query(agent_response)
            query_info["chat_id"] = chat_id

            raw_results = self._execute_qdrant_query(query_info)

            # Trích product_id và gọi ProductServices.get
            products = []
            for pid in raw_results:
                if pid:
                    product = ProductServices.get(pid)
                    if product:
                        products.append(product)
            explanation = self._generate_explanation(query_info, products, user_query, chat_id)
            print(f"Explanation: {explanation}")
            return explanation

        except Exception as e:
            logger.error(f"Lỗi truy vấn Qdrant: {e}")
            return "Đã xảy ra lỗi khi thực hiện truy vấn."

@router.post("/chatbot", response_model=AgentResponse)
async def chatbot_endpoint(request: ChatbotRequest):
    try:
        message = request.message

        # # Lưu tin nhắn vào cơ sở dữ liệu
        # message_repository = MessageRepository()
        # message_payload = CreateMessagePayload(
        #     chat_id=request.chat_id,
        #     role="user",
        #     content=message
        # )
        # message_repository.create(message_payload)
        # Tạo câu hỏi cho agent
        question = f"Người dùng hỏi: {message}"
        agent = QdrantAgent()
        response = await agent.process_query(user_query=question, chat_id=request.chat_id)
        # Lưu phản hồi vào cơ sở dữ liệu
        # response_payload = CreateMessagePayload(
        #     chat_id=request.chat_id,
        #     role="assistant",
        #     content=response
        # )
        # message_repository.create(response_payload)
        return response
    except Exception as e:
        logger.error(f"Lỗi trong chatbot_endpoint: {e}")
        return "Đã xảy ra lỗi khi xử lý yêu cầu."
