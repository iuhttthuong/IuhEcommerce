from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .product_management import ProductManagement, ProductManagementAgent
from .inventory import Inventory
from .marketing import Marketing
from .customer_service import CustomerService
from .analytics import Analytics
from .policy import PolicyAgent
from .chat_repository import ChatRepository
from models.shops import Shop
from models.products import Product, ProductCreate
from models.orders import Order as OrderModel, OrderCreate
from models.customers import Customer, CustomerCreate
from models.promotions import PromotionCreate
from models.chats import ChatMessageCreate, ChatCreate
from .schemas import AnalyticsRequest
from autogen import ConversableAgent, AssistantAgent
from env import env
from db import get_db
from repositories.message import MessageRepository
from services.chat import ChatService
import json
from loguru import logger
from .base import ShopRequest, ChatMessageRequest, process_shop_chat
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ShopManager:
    def __init__(self, db: Session = Depends(get_db), shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.product_mgmt = ProductManagement(db=db)
        self.inventory = Inventory(db, shop_id)
        self.marketing = Marketing(db, shop_id)
        self.customer_service = CustomerService(db, shop_id)
        self.analytics = Analytics(db, shop_id)
        self.policy = PolicyAgent(shop_id=shop_id)
        self.chat_repo = ChatRepository(db)
        self.message_repo = MessageRepository
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Định nghĩa các agent và chức năng của họ
        self.agent_descriptions = {
            "ProductManagementAgent": {
                "description": """Chuyên về quản lý sản phẩm:
- Thêm, sửa, xóa sản phẩm
- Danh sách sản phẩm
- Thông tin chi tiết sản phẩm
- Thống kê số lượng sản phẩm
- Phân loại sản phẩm""",
                "keywords": ["sản phẩm", "thêm sản phẩm", "sửa sản phẩm", "xóa sản phẩm", "danh sách sản phẩm", "thông tin sản phẩm"],
                "handler": self.product_mgmt.process
            },
            "InventoryAgent": {
                "description": """Chuyên về quản lý tồn kho:
- Nhập/xuất hàng
- Kiểm tra tồn kho
- Cảnh báo hết hàng
- Thống kê tồn kho
- Quản lý kho""",
                "keywords": ["tồn kho", "nhập hàng", "xuất hàng", "kiểm tra kho", "hết hàng", "thống kê kho"],
                "handler": self.inventory.process
            },
            "MarketingAgent": {
                "description": """Chuyên về marketing:
- Khuyến mãi
- Giảm giá
- Quảng cáo
- Chiến dịch
- Tăng doanh số""",
                "keywords": ["marketing", "khuyến mãi", "giảm giá", "quảng cáo", "chiến dịch", "tăng doanh số"],
                "handler": self.marketing.process
            },
            "CustomerServiceAgent": {
                "description": """Chuyên về chăm sóc khách hàng:
- Hỗ trợ khách hàng
- Xử lý khiếu nại
- Đánh giá
- Phản hồi
- Tư vấn""",
                "keywords": ["khách hàng", "hỗ trợ", "khiếu nại", "phàn nàn", "đánh giá", "phản hồi"],
                "handler": self.customer_service.process
            },
            "AnalyticsAgent": {
                "description": """Chuyên về phân tích dữ liệu:
- Báo cáo doanh số
- Thống kê bán hàng
- Phân tích hiệu quả
- Báo cáo tồn kho
- Báo cáo khách hàng""",
                "keywords": ["báo cáo", "thống kê", "doanh số", "phân tích", "hiệu quả", "báo cáo tồn kho"],
                "handler": self.analytics.process
            },
            "PolicyAgent": {
                "description": """Chuyên về chính sách và quy định:
- Chính sách shop
- Quy định bán hàng
- Điều khoản dịch vụ
- Hướng dẫn sử dụng
- Giải đáp thắc mắc""",
                "keywords": ["chính sách", "quy định", "điều khoản", "hướng dẫn", "giải đáp", "thắc mắc"],
                "handler": self.policy.process
            },
            "Myself": {
                "description": """Chuyên xử lý các câu hỏi chung:
- Câu hỏi chào hỏi
- Câu hỏi về thời tiết
- Câu hỏi về thời gian
- Câu hỏi chung khác
- Hỗ trợ tổng quát""",
                "keywords": ["xin chào", "chào", "thời tiết", "mấy giờ", "ngày", "tháng", "năm"],
                "handler": self._handle_general_questions
            }
        }

        # Khởi tạo ConversableAgent cho chat
        config_list = [
            {
                "model": "gpt-4o-mini",
                "api_key": env.OPENAI_API_KEY
            }
        ]

        self.chat_agent = ConversableAgent(
            name="shop_manager",
            system_message=self._get_system_message(),
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

    def _get_system_message(self) -> str:
        """Get system message for chat agent."""
        return """
Bạn là một trợ lý AI thông minh cho hệ thống quản lý shop IUH-Ecommerce.

Nhiệm vụ của bạn:
- Phân tích kỹ câu hỏi/ngữ cảnh của người dùng để xác định đúng ý định (intent) và mục đích thực sự.
- Chọn agent phù hợp nhất để xử lý, dựa trên ý định, không chỉ dựa vào từ khóa.
- Chỉ chuyển sang AnalyticsAgent khi người dùng thực sự yêu cầu các tác vụ liên quan đến báo cáo, thống kê, phân tích dữ liệu (ví dụ: xuất báo cáo, xem thống kê, phân tích hiệu quả...).

Quy trình:
1. Đọc kỹ câu hỏi/ngữ cảnh, xác định ý định chính (ví dụ: hỏi về sản phẩm, tồn kho, marketing, chăm sóc khách hàng, chính sách, hay báo cáo).
2. Nếu ý định là:
   - Quản lý sản phẩm: ProductManagementAgent
   - Quản lý tồn kho: InventoryAgent
   - Marketing/khuyến mãi: MarketingAgent
   - Chăm sóc khách hàng: CustomerServiceAgent
   - Chính sách/quy định: PolicyAgent
   - Báo cáo/thống kê/phân tích: AnalyticsAgent
   - Câu hỏi chung/chào hỏi: Myself
3. Nếu không chắc chắn, hãy hỏi lại người dùng để làm rõ ý định trước khi chọn agent.

Yêu cầu trả về JSON:
{
    "agent": "ProductManagementAgent" | "InventoryAgent" | "MarketingAgent" | "CustomerServiceAgent" | "AnalyticsAgent" | "PolicyAgent" | "Myself",
    "intent": "ý định chính",
    "reason": "giải thích ngắn gọn vì sao chọn agent này",
    "query": "nội dung cần chuyển cho agent"
}

Lưu ý:
- Không chỉ dựa vào từ khóa đơn lẻ.
- Không chuyển sang AnalyticsAgent nếu không phải yêu cầu về báo cáo/thống kê/phân tích.
- Nếu câu hỏi không rõ ràng, hãy trả về agent là Myself và hỏi lại người dùng.
"""

    async def process_chat_message(self, message: str, response: dict, shop_id: int, chat_id: int = None) -> Dict[str, Any]:
        """Process chat message and route to appropriate agent."""
        try:
            # Validate input parameters
            if not isinstance(response, dict):
                logger.warning(f"Invalid response type: {type(response)}. Expected dict.")
                response = {}

            if not shop_id:
                return {
                    "message": "❌ **Lỗi**: Bạn vui lòng cung cấp shop_id hoặc thông tin nhận diện shop.",
                    "type": "error"
                }

            # Get or create chat session
            chat_id = await self._get_or_create_chat_session(shop_id, response.get("chat_id"))
            if not chat_id:
                return {
                    "message": "❌ **Lỗi**: Không thể tạo phiên chat mới.",
                    "type": "error"
                }

            # Get chat history
            chat_history = await self._get_chat_history(chat_id)

            # Nếu là câu hỏi về bản thân AI, luôn trả lời bằng Myself
            ai_self_keywords = ["bạn là ai", "ai đang trả lời", "giới thiệu về bạn", "assistant", "trợ lý"]
            if any(kw in message.lower() for kw in ai_self_keywords):
                result = await self._handle_general_questions(message)
                await self._save_messages_to_history(chat_id, shop_id, message, result)
                return result

            # Analyze message to determine required agents
            agent_analysis = await self._analyze_message_for_agents(message, chat_history)
            responses = []
            last_agent_name = response.get('last_agent') if response else None
            for agent_info in agent_analysis.get('agents', []):
                agent_name = agent_info['agent']
                confidence = agent_info['confidence']
                intent = agent_info.get('intent', '')

                # Nếu agent là Myself, intent là general/chitchat/greeting/other, hoặc agent không hợp lệ thì ShopManager tự trả lời
                if (
                    agent_name == "Myself" or
                    intent in ["general", "greeting", "chitchat", "other"] or
                    agent_name not in self.agent_descriptions
                ):
                    result = await self._handle_general_questions(message)
                    if result and result.get('message'):
                        responses.append(result)
                elif confidence >= 0.6:
                    # Nếu agent khác với agent trước đó, reset context
                    agent_context = response.get('context', {}) if (response and agent_name == last_agent_name) else {}
                    result = await self._process_with_agent(agent_name, {
                        "shop_id": shop_id,
                        "message": message,
                        "chat_history": chat_history,
                        "context": agent_context
                    })
                    if result and result.get('message'):
                        responses.append(result)
            if not responses:
                result = await self._handle_fallback(message, chat_history)
                responses.append(result)
            # Chỉ trả về đúng response của agent cuối cùng (hoặc agent chính)
            final_response = responses[-1]  # lấy response cuối cùng
            await self._save_messages_to_history(chat_id, shop_id, message, final_response)
            return {
                "message": final_response.get("message") or final_response.get("content"),
                "type": final_response.get("type", "text"),
                "data": final_response.get("data", {})
            }
        except Exception as e:
            logger.error(f"Error in process_chat_message: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "❌ **Lỗi**: Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error"
            }

    async def _get_or_create_chat_session(self, shop_id: int, existing_chat_id: Optional[int] = None) -> Optional[int]:
        """Get existing chat session or create new one."""
        try:
            if existing_chat_id:
                return existing_chat_id

            chat_service = ChatService(self.db)
            chat = chat_service.create_session(ChatCreate(shop_id=shop_id))
            return chat.chat_id if chat else None
        except Exception as e:
            logger.error(f"Error getting/creating chat session: {str(e)}")
            return None

    async def _get_chat_history(self, chat_id: int) -> str:
        """Get recent chat history."""
        try:
            messages = self.message_repo.get_recent_messages(chat_id, limit=10)
            return "\n".join([
                f"{'User' if msg.sender_type == 'shop' else 'Assistant'}: {msg.content}"
                for msg in messages
            ])
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return ""

    async def _analyze_message_for_agents(self, message: str, chat_history: str) -> Dict[str, Any]:
        """Analyze message to determine which agents should handle it."""
        try:
            # Create prompt for agent analysis
            prompt = f"""Phân tích câu hỏi và xác định các agent cần xử lý:

Câu hỏi: "{message}"

Ngữ cảnh chat:
{chat_history}

Các agent có sẵn và chức năng của họ:
{json.dumps({k: v['description'] for k, v in self.agent_descriptions.items()}, indent=2, ensure_ascii=False)}

Hãy phân tích và trả về JSON với cấu trúc:
{{
    "agents": [
        {{
            "agent": "Tên_Agent",
            "reason": "Lý do chọn agent này",
            "confidence": 0.9,  # Độ tin cậy từ 0-1
            "keywords": ["từ khóa 1", "từ khóa 2"],  # Các từ khóa quan trọng
            "intent": "Ý định chính của người dùng"
        }}
    ],
    "requires_multiple_agents": true/false,  # Có cần nhiều agent không
    "primary_intent": "Ý định chính của người dùng",
    "secondary_intents": ["Ý định phụ 1", "Ý định phụ 2"]
}}"""

            # Get analysis from LLM
            analysis = await self._get_llm_analysis(prompt)
            
            # Parse and validate analysis
            try:
                result = json.loads(analysis)
                if not isinstance(result, dict) or 'agents' not in result:
                    raise ValueError("Invalid analysis format")
                if not result['agents'] or all(a['confidence'] < 0.6 for a in result['agents']):
                    result['agents'] = [{
                        "agent": "Myself",
                        "reason": "Câu hỏi chung hoặc không liên quan đến các agent khác",
                        "confidence": 1.0,
                        "keywords": [],
                        "intent": "general"
                    }]
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    if not isinstance(result, dict) or 'agents' not in result:
                        raise ValueError("Invalid analysis format")
                    if not result['agents'] or all(a['confidence'] < 0.6 for a in result['agents']):
                        result['agents'] = [{
                            "agent": "Myself",
                            "reason": "Câu hỏi chung hoặc không liên quan đến các agent khác",
                            "confidence": 1.0,
                            "keywords": [],
                            "intent": "general"
                        }]
                    return result
                raise ValueError("Could not parse analysis as JSON")
                
        except Exception as e:
            logger.error(f"Error in _analyze_message_for_agents: {str(e)}")
            # Return default analysis with general agent
            return {
                "agents": [{
                    "agent": "CustomerServiceAgent",
                    "reason": "Fallback to general support",
                    "confidence": 0.5,
                    "keywords": [],
                    "intent": "general_support"
                }],
                "requires_multiple_agents": False,
                "primary_intent": "general_support",
                "secondary_intents": []
            }

    async def _process_with_agent(self, agent_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with specific agent."""
        try:
            agent_info = self.agent_descriptions.get(agent_name)
            if not agent_info:
                return {
                    "message": f"❌ Không tìm thấy agent {agent_name}",
                    "type": "error"
                }

            handler = agent_info['handler']
            if not handler:
                return {
                    "message": f"❌ Agent {agent_name} không có handler",
                    "type": "error"
                }

            # Process request with agent
            result = await handler(request)
            if not result:
                return {
                    "message": f"❌ Không thể xử lý yêu cầu với {agent_name}",
                    "type": "error"
                }

            return result

        except Exception as e:
            logger.error(f"Error processing with agent {agent_name}: {str(e)}")
            return {
                "message": f"❌ Đã có lỗi xảy ra khi xử lý yêu cầu: {str(e)}",
                "type": "error"
            }

    async def _handle_fallback(self, message: str, chat_history: str) -> Dict[str, Any]:
        """Handle fallback when no agent is confident enough."""
        try:
            # Create prompt for fallback analysis
            prompt = f"""Phân tích câu hỏi và đưa ra phản hồi phù hợp:

Câu hỏi: "{message}"

Ngữ cảnh chat:
{chat_history}

Các chức năng có sẵn:
1. Quản lý sản phẩm:
   - Xem danh sách sản phẩm
   - Thống kê sản phẩm
   - Chi tiết sản phẩm
   - Phân tích hiệu quả
   - Tối ưu sản phẩm

2. Quản lý tồn kho:
   - Kiểm tra tồn kho
   - Nhập/xuất hàng
   - Cảnh báo hết hàng

3. Marketing:
   - Khuyến mãi
   - Giảm giá
   - Quảng cáo

4. Chăm sóc khách hàng:
   - Hỗ trợ
   - Xử lý khiếu nại
   - Đánh giá

5. Báo cáo:
   - Doanh số
   - Thống kê
   - Phân tích

Hãy phân tích và trả lời:
1. Xác định ý định chính của người dùng
2. Xác định chức năng phù hợp để xử lý
3. Đưa ra phản hồi trực tiếp và chính xác
4. Nếu không hiểu rõ, hỏi lại người dùng một cách cụ thể"""

            # Get response from LLM
            response = await self._get_llm_analysis(prompt)
            
            return {
                "message": response,
                "type": "text",
                "requires_clarification": True
            }

        except Exception as e:
            logger.error(f"Error in _handle_fallback: {str(e)}")
            return {
                "message": "Xin lỗi, tôi không hiểu rõ yêu cầu của bạn. Bạn có thể diễn đạt lại không?",
                "type": "text",
                "requires_clarification": True
            }

    async def _combine_agent_responses(self, responses: List[Dict[str, Any]], query: str, chat_history: str) -> Dict[str, Any]:
        """Combine responses from multiple agents."""
        try:
            # Create prompt for combining responses
            prompt = f"""Kết hợp các câu trả lời từ nhiều agent:

Câu hỏi của người dùng: "{query}"

Ngữ cảnh chat:
{chat_history}

Các câu trả lời cần kết hợp:
{json.dumps([r.get('message', '') for r in responses], indent=2, ensure_ascii=False)}

Hãy tạo một câu trả lời tổng hợp:
1. Tóm tắt các điểm chính
2. Loại bỏ thông tin trùng lặp
3. Sắp xếp thông tin logic
4. Đảm bảo tính nhất quán
5. Giữ lại các chi tiết quan trọng

Trả về câu trả lời tổng hợp dưới dạng văn bản."""

            # Get combined response from LLM
            combined_response = await self._get_llm_analysis(prompt)
            
            return {
                "message": combined_response,
                "type": "text",
                "source_agents": [r.get('type', 'unknown') for r in responses]
            }
            
        except Exception as e:
            logger.error(f"Error combining agent responses: {str(e)}")
            # Return the first response if combination fails
            return responses[0] if responses else {
                "message": "Xin lỗi, đã có lỗi xảy ra khi kết hợp thông tin. Vui lòng thử lại sau.",
                "type": "error"
            }

    async def _get_llm_analysis(self, prompt: str) -> str:
        """Get analysis from LLM."""
        try:
            # Create temporary agent for analysis
            config_list = [
                {
                    "model": "gpt-4o-mini",
                    "api_key": env.OPENAI_API_KEY
                }
            ]
            
            temp_agent = AssistantAgent(
                name="AnalysisAgent",
                system_message="""Bạn là một trợ lý AI chuyên phân tích và xử lý thông tin.
Nhiệm vụ của bạn là phân tích câu hỏi và tạo câu trả lời phù hợp.
Hãy trả lời ngắn gọn, chính xác và hữu ích.""",
                llm_config={"config_list": config_list}
            )
            
            # Get response from LLM
            response = await temp_agent.a_generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response if response else ""
            
        except Exception as e:
            logger.error(f"Error getting LLM analysis: {str(e)}")
            return ""

    async def _save_messages_to_history(self, chat_id: int, shop_id: int, user_message: str, agent_response: Dict[str, Any]) -> None:
        """Save messages to chat history."""
        try:
            # Save user message
            user_msg = ChatMessageCreate(
                chat_id=chat_id,
                sender_type="shop",
                sender_id=shop_id,
                content=user_message
            )
            # self.message_repo.create_message(user_msg)

            # Save agent response
            agent_msg = ChatMessageCreate(
                chat_id=chat_id,
                sender_type="agent_response",
                sender_id=shop_id,
                content=agent_response.get('message', ''),
                message_metadata={
                    "type": agent_response.get('type', 'text'),
                    "data": agent_response.get('data', {})
                }
            )
            # self.message_repo.create_message(agent_msg)

        except Exception as e:
            logger.error(f"Error saving messages to history: {str(e)}")

    async def process_request(self, request: ShopRequest) -> Dict[str, Any]:
        """Process a shop management request."""
        try:
            # Route to appropriate handler based on request type
            if "inventory" in request.message.lower():
                return await self.inventory.process_request(request.dict())
            elif "marketing" in request.message.lower():
                return await self.marketing.process_request(request.dict())
            elif "customer" in request.message.lower():
                return await self.customer_service.process_request(request.dict())
            elif "product" in request.message.lower():
                return await self.product_mgmt.process_request(request.dict())
            elif "policy" in request.message.lower():
                return await self.policy.process(request)
            else:
                # Default to general shop chat
                return await process_shop_chat(request)
        except Exception as e:
            logger.error(f"Error in process_request: {str(e)}")
            return {
                "message": "Đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error",
                "error": str(e)
            }

    async def create_product(self, product_data: dict) -> dict:
        """Create a new product"""
        return await self.product_mgmt.process_request({"message": "thêm sản phẩm", "product_data": product_data})

    async def update_product(self, product_id: int, update_data: dict) -> dict:
        """Update product information"""
        return await self.product_mgmt.process_request({"message": "cập nhật sản phẩm", "product_id": product_id, "update_data": update_data})

    async def delete_product(self, product_id: int) -> dict:
        """Delete a product"""
        return await self.product_mgmt.process_request({"message": "xóa sản phẩm", "product_id": product_id})

    async def get_product(self, product_id: int) -> dict:
        """Get product details"""
        return await self.product_mgmt.process_request({"message": f"chi tiết id: {product_id}"})

    async def list_products(self, shop_id: int) -> dict:
        """List all products for a shop"""
        return await self.product_mgmt.process_request({"message": "danh sách sản phẩm", "shop_id": shop_id})

    async def search_products(self, keyword: str, shop_id: int) -> dict:
        """Search products by keyword"""
        return await self.product_mgmt.process_request({"message": "tìm kiếm sản phẩm", "keyword": keyword, "shop_id": shop_id})

    async def update_order_status(self, order_id: int, status: str) -> OrderModel:
        """Update order status"""
        return await self.order_mgmt.update_order_status(order_id, status)

    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer"""
        return await self.customer_service.create_customer(customer_data)

    async def get_customer(self, customer_id: int) -> Customer:
        """Get customer details"""
        return await self.customer_service.get_customer(customer_id)

    async def create_marketing_campaign(self, campaign_data: PromotionCreate) -> Dict[str, Any]:
        """Create a new marketing campaign"""
        return await self.marketing.create_campaign(campaign_data)

    async def get_analytics(self, request: AnalyticsRequest) -> Dict[str, Any]:
        """Get shop analytics"""
        return await self.analytics.get_analytics(request)

    async def get_shop_summary(self) -> Dict[str, Any]:
        """Get shop summary including key metrics"""
        return {
            "total_products": await self.product_mgmt.get_total_products(),
            "total_customers": await self.customer_service.get_total_customers(),
            "inventory_value": await self.inventory.get_total_inventory_value()
        }

    async def _handle_general_questions(self, message: str) -> dict:
        # Trả lời ngắn gọn, thân thiện cho các intent chào hỏi, hỏi chung
        greetings = [
            "xin chào", "chào bạn", "hello", "hi", "hey", "alo", "bạn là ai", "trợ lý", "assistant"
        ]
        if any(greet in message.lower() for greet in greetings):
            return {
                "message": """Tôi là trợ lý AI của hệ thống quản lý shop IUH-Ecommerce.\n
                        Tôi có thể hỗ trợ bạn về sản phẩm, tồn kho, marketing, khách hàng, chính sách, báo cáo và nhiều nghiệp vụ khác.\n
                        Bạn chỉ cần đặt câu hỏi hoặc yêu cầu, tôi sẽ giúp bạn giải quyết nhanh nhất!""",
                "type": "text"
            }
        # Nếu không phải chào hỏi, trả về câu trả lời mặc định
        return {
            "message": "Cảm ơn bạn đã trò chuyện! Nếu bạn cần hỗ trợ gì về shop, hãy đặt câu hỏi nhé!",
            "type": "text"
            } 