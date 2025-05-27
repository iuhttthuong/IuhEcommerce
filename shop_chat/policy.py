from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os, json, dotenv
from autogen import AssistantAgent, ConversableAgent
import uuid
from db import Session
from models.fqas import FQA
from repositories.message import MessageRepository
from controllers.search import search
import traceback
from models.chats import ChatMessageCreate
from autogen import register_function
from env import env
from services.policy import PolicyService
from embedding.main import COLLECTIONS
import logging
from services.search import SearchServices
from typing import Optional, Dict, Any, List
from .base import BaseShopAgent, ShopRequest, ChatMessageRequest
from datetime import datetime
from loguru import logger
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Lấy cấu hình model từ môi trường
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": env.OPENAI_API_KEY
    }
]

class AgentMessage(BaseModel):
    agent_id: str
    agent_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatbotRequest(BaseModel):
    chat_id: int
    message: str
    context: Optional[dict] = None
    user_id: Optional[int] = None
    shop_id: Optional[int] = None
    entities: Optional[Dict[str, Any]] = None
    agent_messages: Optional[List[AgentMessage]] = None
    filters: Optional[Dict[str, Any]] = None

router = APIRouter(prefix="/shop/policy", tags=["Shop Policy"])

OPTIMAL_SYSTEM_MESSAGE = '''
Bạn là chuyên gia AI về chính sách cho sàn thương mại điện tử IUH-Ecommerce, chuyên tư vấn, giải thích, hướng dẫn chi tiết cho người bán về mọi chính sách, quy định, thủ tục của sàn.

YÊU CẦU:
- Luôn ưu tiên sử dụng thông tin chính sách từ hệ thống (FAQ, embedding, context, luật mới nhất) để trả lời.
- Nếu context chưa đủ, hãy hỏi lại để lấy thêm thông tin hoặc chủ động tìm kiếm web, nhưng phải giải thích rõ nguồn và liên hệ thực tế với shop.
- Trả lời chi tiết, đúng trọng tâm, có ví dụ, hướng dẫn từng bước nếu cần.
- Ưu tiên lợi ích người bán, nhưng luôn đảm bảo tuân thủ quy định sàn.
- Không trả lời chung chung, không lý thuyết suông.

CẤU TRÚC TRẢ LỜI (nên tham khảo):
1. Chi tiết chính sách liên quan
2. Điều kiện & quy định
3. Quy trình thực hiện
4. Lưu ý quan trọng
5. Khuyến nghị cho shop
'''

class PolicyAgent(BaseShopAgent):
    def __init__(self, shop_id: int = None):
        super().__init__(
            shop_id=shop_id,
            name="PolicyAgent",
            system_message=OPTIMAL_SYSTEM_MESSAGE
        )
        self.message_repository = MessageRepository()
        self.agent_name = "PolicyAgent"

    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        try:
            query = request.message
            logger.info(f"PolicyAgent received query: {query}")

            # Lưu tin nhắn vào DB
            message_payload = ChatMessageCreate(
                chat_id=request.chat_id if hasattr(request, 'chat_id') else 0,
                sender_type="user",
                sender_id=0,
                content=query
            )
            self.message_repository.create_message(message_payload)

            # Semantic search context chính sách
            search_results = SearchServices.search(query, collection_name="faq_embeddings", limit=5)
            logger.info(f"PolicyAgent search results: {search_results}")

            # Tổng hợp context ưu tiên answer/text_content
            context_list = []
            if search_results and isinstance(search_results[0], dict):
                for result in search_results:
                    payload = result.get("payload", {})
                    answer = payload.get("answer", "")
                    text_content = payload.get("text_content", "")
                    if answer:
                        context_list.append(f"- {answer}")
                    elif text_content:
                        context_list.append(f"- {text_content}")
            context = "\n".join(context_list)

            # Nếu context yếu hoặc chỉ có 1 câu trả lời ngắn, ép LLM phân tích sâu và chủ động search web
            need_web = False
            if not context or len(context) < 30 or (len(context_list) == 1 and len(context_list[0]) < 80):
                need_web = True

            web_results = None
            if need_web:
                try:
                    web_results = await web_search(
                        search_term=f"{query} site:gov.vn OR site:moit.gov.vn OR site:luatvietnam.vn OR site:baochinhphu.vn",
                        explanation="Tìm kiếm thông tin chính sách mới nhất, chuyên sâu từ các nguồn uy tín để bổ sung cho câu trả lời."
                    )
                except Exception as e:
                    logger.warning(f"Web search failed: {e}")
                    web_results = None

            if not context or len(context) < 30:
                response_content = (
                    "Xin lỗi, tôi chưa tìm thấy thông tin chính sách phù hợp với câu hỏi của bạn trong hệ thống. "
                    "Dưới đây là thông tin tôi thu thập được từ các nguồn bên ngoài:\n"
                    f"{web_results.results if web_results and hasattr(web_results, 'results') else web_results}"
                )
            else:
                # Tạo prompt cho LLM
                prompt = (
                    f"Câu hỏi của người bán: {query}\n"
                    "Dưới đây là các chính sách thực tế của các sàn thương mại điện tử lớn tại Việt Nam (Shopee, Lazada, Tiki, ...), bạn hãy tổng hợp, so sánh, và trả lời như chính sách của IUH-Ecommerce, ưu tiên lợi ích người bán, nhưng đảm bảo tuân thủ quy định chung:\n"
                    f"{context}\n"
                )
                if need_web and web_results:
                    prompt += f"\nKết quả tìm kiếm web liên quan: {web_results.results if hasattr(web_results, 'results') else web_results}\n"
                prompt += (
                    "---\n"
                    "Hãy trả lời thật chuyên sâu, phân tích kỹ, mở rộng, lấy ví dụ thực tế, hướng dẫn từng bước nếu cần. Nếu phải dùng thông tin ngoài, hãy giải thích rõ nguồn và liên hệ thực tế với shop."
                )
                # response_content = call_gpt4o_mini(self.system_message, prompt)
                response_content = "[GPT-4o-mini trả lời ở đây: tổng hợp, so sánh chính sách các sàn lớn, trả lời như IUH-Ecommerce]"  # Placeholder

            # Lưu phản hồi vào DB
            response_payload = ChatMessageCreate(
                chat_id=request.chat_id if hasattr(request, 'chat_id') else 0,
                sender_type="assistant",
                sender_id=0,
                content=response_content
            )
            self.message_repository.create_message(response_payload)

            formatted_response = {
                "title": f"Chính sách liên quan đến: {query[:30]}...",
                "content": response_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return {
                "response": formatted_response,
                "agent": self.agent_name,
                "context": {
                    "search_results": search_results if 'search_results' in locals() else [],
                    "shop_id": request.shop_id if hasattr(request, 'shop_id') else None,
                    "web_results": web_results
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in PolicyAgent.process: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_message = "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ shop."
            return {
                "response": {
                    "title": "Lỗi xử lý yêu cầu",
                    "content": error_message,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "agent": self.agent_name,
                "context": {},
                "timestamp": datetime.now().isoformat()
            }

@router.post("/query")
async def query_policy(request: ChatMessageRequest):
    try:
        agent = PolicyAgent(shop_id=request.sender_id if request.sender_type == "shop" else None)
        shop_request = ShopRequest(
            message=request.content,
            chat_id=request.chat_id,
            shop_id=request.sender_id if request.sender_type == "shop" else None,
            user_id=None,
            context=request.message_metadata if request.message_metadata else {},
            entities={},
            agent_messages=[],
            filters={}
        )
        response = await agent.process(shop_request)
        return response
    except Exception as e:
        logger.error(f"Error in query_policy: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

def search_faq(query: str, limit: int = 1):
    results = SearchServices.search(query, collection_name="faq_embeddings", limit=limit)
    if results and isinstance(results[0], dict):
        payload = results[0].get("payload")
        if payload and "answer" in payload:
            return payload["answer"]
    return "Xin lỗi, tôi không tìm thấy thông tin liên quan đến câu hỏi của bạn."

def get_fqa(payload: str, collection_name: str = "faq_embeddings", limit: int = 1):
    return search_faq(payload, limit)

@router.get("/faq")
def get_policy_faq(query: str, limit: int = 1):
    answer = search_faq(query, limit)
    return {"answer": answer}

async def web_search(search_term: str, explanation: str = None) -> Dict[str, Any]:
    """Search the web for information"""
    try:
        # Thực hiện tìm kiếm web
        search_url = f"https://www.google.com/search?q={search_term}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy kết quả tìm kiếm
        search_results = []
        for result in soup.find_all('div', class_='g')[:5]:  # Lấy 5 kết quả đầu tiên
            title = result.find('h3')
            link = result.find('a')
            snippet = result.find('div', class_='VwiC3b')
            
            if title and link and snippet:
                search_results.append({
                    'title': title.text,
                    'link': link['href'],
                    'snippet': snippet.text
                })
        
        return {
            'results': search_results,
            'explanation': explanation
        }
    except Exception as e:
        logger.error(f"Error in web_search: {str(e)}")
        return {
            'results': [],
            'error': str(e)
        } 