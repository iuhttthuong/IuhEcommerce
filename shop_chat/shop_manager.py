from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .product_management import ProductManagement, ProductManagementAgent
from .inventory import Inventory
from .marketing import Marketing
from .customer_service import CustomerService
from .analytics import Analytics
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

class ShopManager:
    def __init__(self, db: Session = Depends(get_db), shop_id: int = None):
        self.db = db
        self.shop_id = shop_id
        self.product_mgmt = ProductManagement(db=db)
        self.inventory = Inventory(db, shop_id)
        self.marketing = Marketing(db, shop_id)
        self.customer_service = CustomerService(db, shop_id)
        self.analytics = Analytics(db, shop_id)
        self.chat_repo = ChatRepository(db)
        self.message_repo = MessageRepository
        self.agent_descriptions = {
            "ProductManagementAgent": """Chuyên về quản lý sản phẩm:
- Thêm, sửa, xóa sản phẩm
- Danh sách sản phẩm
- Thông tin chi tiết sản phẩm
- Thống kê số lượng sản phẩm
- Phân loại sản phẩm""",
            "InventoryAgent": """Chuyên về quản lý tồn kho:
- Nhập/xuất hàng
- Kiểm tra tồn kho
- Cảnh báo hết hàng
- Thống kê tồn kho
- Quản lý kho""",
            "MarketingAgent": """Chuyên về marketing:
- Khuyến mãi
- Giảm giá
- Quảng cáo
- Chiến dịch
- Tăng doanh số""",
            "CustomerServiceAgent": """Chuyên về chăm sóc khách hàng:
- Hỗ trợ khách hàng
- Xử lý khiếu nại
- Đánh giá
- Phản hồi
- Tư vấn""",
            "AnalyticsAgent": """Chuyên về phân tích dữ liệu:
- Báo cáo doanh số
- Thống kê bán hàng
- Phân tích hiệu quả
- Báo cáo tồn kho
- Báo cáo khách hàng"""
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
            system_message="""
Bạn là một trợ lý AI thông minh làm việc cho shop trên sàn thương mại điện tử IUH-Ecomerce.
Bạn sẽ nhận đầu vào câu hỏi của chủ shop về quản lý shop.
Nhiệm vụ của bạn là PHÂN TÍCH KỸ câu hỏi để hiểu rõ ý định của người dùng và chọn agent phù hợp nhất để xử lý.

QUY TRÌNH PHÂN TÍCH CÂU HỎI:
1. Xác định chủ đề chính
2. Phân tích ngữ cảnh và mục đích
3. Xác định các yêu cầu cụ thể
4. Chọn agent phù hợp nhất

CÁC LOẠI CÂU HỎI VÀ AGENT TƯƠNG ỨNG:

1. Câu hỏi về khiếu nại/phàn nàn của khách hàng:
   - "Khách hàng phàn nàn về..."
   - "Có người kêu sản phẩm..."
   - "Khách hàng báo lỗi..."
   => Sử dụng CustomerServiceAgent

2. Câu hỏi về đánh giá sản phẩm:
   - "Đánh giá sản phẩm..."
   - "Review sản phẩm..."
   - "Khách hàng đánh giá..."
   => Sử dụng AnalyticsAgent

3. Câu hỏi về quản lý sản phẩm:
   - "Thêm/sửa/xóa sản phẩm"
   - "Danh sách sản phẩm"
   - "Thông tin sản phẩm"
   => Sử dụng ProductManagementAgent

4. Câu hỏi về tồn kho:
   - "Kiểm tra tồn kho"
   - "Nhập/xuất hàng"
   - "Hết hàng"
   => Sử dụng InventoryAgent

5. Câu hỏi về marketing:
   - "Khuyến mãi"
   - "Giảm giá"
   - "Quảng cáo"
   => Sử dụng MarketingAgent

6. Câu hỏi về báo cáo/phân tích:
   - "Thống kê doanh số"
   - "Báo cáo bán hàng"
   - "Phân tích hiệu quả"
   => Sử dụng AnalyticsAgent

Hãy trả về JSON với cấu trúc:
{
    "agent": "ProductManagementAgent" | "InventoryAgent" | "MarketingAgent" | "CustomerServiceAgent" | "AnalyticsAgent" | "PolicyAgent",
    "query": String,
    "intent": String,
    "context": {
        "topic": String,
        "specific_requirements": [String]
    }
}

VÍ DỤ PHÂN TÍCH:

1. "Có khách hàng phàn nàn sản phẩm của tôi kém chất lượng, tôi nên làm gì?"
=> {
    "agent": "CustomerServiceAgent",
    "query": "Xử lý phàn nàn về chất lượng sản phẩm",
    "intent": "handle_complaint",
    "context": {
        "topic": "customer_complaint",
        "specific_requirements": ["quality_issue", "complaint_handling", "customer_satisfaction"]
    }
}

2. "Shop tôi có bao nhiêu đơn hàng trong tháng này?"
=> {
    "agent": "AnalyticsAgent",
    "query": "Thống kê số lượng đơn hàng theo tháng",
    "intent": "sales_analysis",
    "context": {
        "topic": "order_statistics",
        "specific_requirements": ["order_count", "monthly_report"]
    }
}

LƯU Ý QUAN TRỌNG:
1. PHÂN TÍCH KỸ câu hỏi trước khi chọn agent
2. Xem xét ngữ cảnh và mục đích thực sự
3. KHÔNG chỉ dựa vào từ khóa đơn lẻ
4. Chọn agent phù hợp nhất với yêu cầu
5. Đảm bảo response đúng trọng tâm câu hỏi
            """,
            llm_config={"config_list": config_list},
            human_input_mode="NEVER"
        )

    async def process_chat_message(self, message: str, response: dict, shop_id: int, chat_id: int = None) -> Dict[str, Any]:
        try:
            # Validate input parameters
            if not isinstance(response, dict):
                logger.warning(f"Invalid response type: {type(response)}. Expected dict.")
                response = {}  # Initialize empty dict if response is invalid

            if shop_id:
                shop_id = int(shop_id)
            else:
                return {
                    "message": "❌ **Lỗi**: Bạn vui lòng cung cấp shop_id hoặc thông tin nhận diện shop để tôi có thể lấy danh sách sản phẩm.",
                    "type": "error",
                    "data": {
                        "response": "",
                        "agent": "ProductManagementAgent",
                        "timestamp": datetime.now().isoformat()
                    }
                }

            # Lấy chat_id từ response hoặc tạo mới nếu không có
            if not chat_id:
                # Đảm bảo response là dict và không phải None
                if response is None:
                    response = {}
            chat_id = response.get("chat_id")
            if not chat_id:
                # Tạo session chat mới nếu chưa có
                chat_service = ChatService(self.db)
                chat = chat_service.create_session(ChatCreate(shop_id=shop_id))
                chat_id = chat.chat_id

            # Lấy lịch sử chat gần nhất (10 tin nhắn)
            chat_history = self.message_repo.get_recent_messages(chat_id, limit=10)
            chat_context = "\n".join([
                f"{'User' if msg.sender_type == 'shop' else 'Assistant'}: {msg.content}"
                for msg in chat_history
            ])

            # Get agent and query from response with safe defaults
            if response is None:
                response = {}
            agent = response.get("agent", "ProductManagementAgent")  # Default to ProductManagementAgent
            query = response.get("query", message)  # Default to original message
            # Đảm bảo response.get("response", {}) không bị lỗi nếu response là None
            resp_content = response.get("response", {}) if response else {}
            content = resp_content.get("content", "") if isinstance(resp_content, dict) else ""

            # Handle content based on its type
            if isinstance(content, dict):
                # If content is already a dictionary, use it directly
                agent = content.get("agent") or agent
                query = content.get("query") or query
            elif isinstance(content, str):
                # If content is a string, try to parse it as JSON
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    try:
                        content_dict = json.loads(content)
                        agent = content_dict.get("agent") or agent
                        query = content_dict.get("query") or query
                    except json.JSONDecodeError as e:
                        logger.warning(f"Content appears to be JSON but failed to parse: {e}")
                        # If JSON parsing fails, use the content as query
                        query = query or content
                else:
                    # If content doesn't look like JSON, use it as query
                    query = query or content
            else:
                # For any other type, use the original query
                query = message

            # Ensure we have a valid query
            if not query:
                query = message

            # Analyze message to determine required agents
            agent_analysis = await self._analyze_message_for_agents(query, chat_context)
            
            # Process with identified agents
            responses = []
            for agent_info in agent_analysis.get('agents', []):
                agent_name = agent_info['agent']
                confidence = agent_info['confidence']
                
                # Only process with agents that have high confidence
                if confidence >= 0.6:
                    result = await self._process_with_agent(agent_name, {
                        "shop_id": shop_id,
                        "message": query,
                        "chat_history": chat_context
                    })
                    if result and result.get('message'):
                        responses.append(result)

            # If no high-confidence responses, use the original agent
            if not responses:
                result = await self._process_with_agent(agent, {
                    "shop_id": shop_id,
                    "message": query,
                    "chat_history": chat_context
                })
                if result and result.get('message'):
                    responses.append(result)

            # Combine responses if multiple agents were used
            if len(responses) > 1:
                combined_response = await self._combine_agent_responses(responses, query, chat_context)
                result = combined_response
            elif responses:
                result = responses[0]
            else:
                # Nếu không có phản hồi phù hợp, phân tích câu hỏi để đưa ra phản hồi chính xác hơn
                prompt = f"""Phân tích câu hỏi của người dùng và đưa ra phản hồi phù hợp:

Câu hỏi: "{query}"

Ngữ cảnh chat:
{chat_context}

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
4. Nếu không hiểu rõ, hỏi lại người dùng một cách cụ thể

Trả về JSON với cấu trúc:
{{
    "message": "Câu trả lời",
    "type": "text/error/confirmation",
    "requires_clarification": true/false,
    "clarification_question": "Câu hỏi làm rõ (nếu cần)",
    "suggested_actions": ["Hành động 1", "Hành động 2"],
    "related_topics": ["Chủ đề 1", "Chủ đề 2"]
}}"""

                try:
                    # Sử dụng LLM để phân tích và tạo phản hồi
                    analysis = await self._get_llm_analysis(prompt)
                    result = json.loads(analysis)
                    
                    # Thêm các hành động gợi ý nếu có
                    if result.get('suggested_actions'):
                        result['message'] += "\n\n💡 **Bạn có thể**:\n" + "\n".join(
                            f"- {action}" for action in result['suggested_actions']
                        )
                    
                    # Thêm các chủ đề liên quan nếu có
                    if result.get('related_topics'):
                        result['message'] += "\n\n🔍 **Chủ đề liên quan**:\n" + "\n".join(
                            f"- {topic}" for topic in result['related_topics']
                        )
                        
                except Exception as e:
                    logger.error(f"Error analyzing query: {str(e)}")
                    # Phân tích câu hỏi để đưa ra phản hồi phù hợp
                    if "sản phẩm" in query.lower():
                        result = {
                            "message": "📋 **Danh sách chức năng quản lý sản phẩm**:\n\n"
                                     "1. Xem danh sách sản phẩm\n"
                                     "2. Thống kê sản phẩm\n"
                                     "3. Xem chi tiết sản phẩm\n"
                                     "4. Phân tích hiệu quả\n"
                                     "5. Tối ưu sản phẩm\n\n"
                                     "❓ **Bạn muốn thực hiện chức năng nào?**",
                            "type": "text",
                            "requires_clarification": True,
                            "clarification_question": "Bạn muốn thực hiện chức năng nào trong danh sách trên?"
                        }
                    elif "tồn kho" in query.lower() or "kho" in query.lower():
                        result = {
                            "message": "📦 **Danh sách chức năng quản lý tồn kho**:\n\n"
                                     "1. Kiểm tra tồn kho\n"
                                     "2. Nhập/xuất hàng\n"
                                     "3. Cảnh báo hết hàng\n\n"
                                     "❓ **Bạn muốn thực hiện chức năng nào?**",
                            "type": "text",
                            "requires_clarification": True,
                            "clarification_question": "Bạn muốn thực hiện chức năng nào trong danh sách trên?"
                        }
                    elif "marketing" in query.lower() or "khuyến mãi" in query.lower():
                        result = {
                            "message": "🎯 **Danh sách chức năng marketing**:\n\n"
                                     "1. Tạo khuyến mãi\n"
                                     "2. Quản lý giảm giá\n"
                                     "3. Tạo quảng cáo\n\n"
                                     "❓ **Bạn muốn thực hiện chức năng nào?**",
                            "type": "text",
                            "requires_clarification": True,
                            "clarification_question": "Bạn muốn thực hiện chức năng nào trong danh sách trên?"
                        }
                    else:
                        result = {
                            "message": "ℹ️ **Danh sách chức năng chính**:\n\n"
                                     "1. 📋 Quản lý sản phẩm\n"
                                     "2. 📦 Quản lý tồn kho\n"
                                     "3. 🎯 Marketing\n"
                                     "4. 👥 Chăm sóc khách hàng\n"
                                     "5. 📊 Báo cáo\n\n"
                                     "❓ **Bạn muốn sử dụng chức năng nào?**",
                            "type": "text",
                            "requires_clarification": True,
                            "clarification_question": "Bạn muốn sử dụng chức năng nào trong danh sách trên?"
                        }

            # Format response message in markdown
            if result.get('message'):
                # Format statistics
                if 'total_products' in result:
                    result['message'] = f"📊 **Thống kê sản phẩm**:\n{result['message']}"
                # Format product list
                if 'products' in result:
                    result['message'] = f"📋 **Danh sách sản phẩm**:\n{result['message']}"
                # Format inventory
                if 'inventory' in result:
                    result['message'] = f"📦 **Thông tin tồn kho**:\n{result['message']}"
                # Format error
                if result.get('type') == 'error':
                    result['message'] = f"❌ **Lỗi**: {result['message']}"
                # Format success
                if result.get('type') == 'success':
                    result['message'] = f"✅ **Thành công**: {result['message']}"
                # Format confirmation
                if result.get('type') == 'confirmation':
                    result['message'] = f"ℹ️ **Xác nhận**: {result['message']}"
                # Format clarification request
                if result.get('requires_clarification'):
                    result['message'] = f"{result['message']}\n\n❓ **Cần làm rõ**: {result.get('clarification_question', 'Bạn có thể cung cấp thêm thông tin không?')}"

            # Lưu tin nhắn vào lịch sử chat
            try:
                # Lưu tin nhắn của shop
                shop_message = ChatMessageCreate(
                    chat_id=chat_id,
                    sender_type="shop",
                    sender_id=shop_id,
                    content=message,
                    message_metadata={"agent": agent, "query": query}
                )
                # self.message_repo.create_message(shop_message)

                # Serialize the result data to ensure it's JSON compatible
                serialized_result = {
                    "message": result.get('message', ''),
                    "type": result.get('type', 'text'),
                    "data": {}
                }

                # Handle products data if present
                if "products" in result:
                    serialized_result["data"]["products"] = [
                        {
                            "product_id": p.get("product_id"),
                            "name": p.get("name"),
                            "price": float(p.get("price", 0)) if p.get("price") is not None else 0,
                            "current_stock": int(p.get("current_stock", 0)) if p.get("current_stock") is not None else 0,
                            "quantity_sold": int(p.get("quantity_sold", 0)) if p.get("quantity_sold") is not None else 0,
                            "rating_average": float(p.get("rating_average", 0)) if p.get("rating_average") is not None else 0,
                            "review_count": int(p.get("review_count", 0)) if p.get("review_count") is not None else 0,
                            "category": p.get("category", {}).get("name") if isinstance(p.get("category"), dict) else str(p.get("category"))
                        }
                        for p in result.get("products", [])
                    ]

                # Handle other metrics if present
                for key in ["total_products", "total_value", "total_sold", "avg_rating", "total_reviews"]:
                    if key in result:
                        value = result[key]
                        if isinstance(value, (int, float, str, bool)):
                            serialized_result["data"][key] = value
                        else:
                            try:
                                serialized_result["data"][key] = float(value)
                            except (TypeError, ValueError):
                                serialized_result["data"][key] = str(value)

                # Lưu phản hồi của agent
                agent_message = ChatMessageCreate(
                    chat_id=chat_id,
                    sender_type="agent_response",
                    sender_id=shop_id,
                    content=result.get('message', ''),
                    message_metadata={
                        "agent_type": agent,
                        "response_data": serialized_result
                    }
                )
                # self.message_repo.create_message(agent_message)

            except Exception as e:
                logger.error(f"Error saving messages: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")

            return result

        except Exception as e:
            logger.error(f"Error in process_chat_message: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": "❌ **Lỗi**: Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
                "type": "error"
            }

    async def _analyze_message_for_agents(self, message: str, chat_history: str) -> Dict[str, Any]:
        """Analyze message to determine which agents should handle it."""
        try:
            # Create prompt for agent analysis
            prompt = f"""Phân tích câu hỏi và xác định các agent cần xử lý:

Câu hỏi: "{message}"

Ngữ cảnh chat:
{chat_history}

Các agent có sẵn và chức năng của họ:
{json.dumps(self.agent_descriptions, indent=2, ensure_ascii=False)}

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
}}

Lưu ý:
- Một câu hỏi có thể cần nhiều agent
- Độ tin cậy càng cao càng phù hợp
- Phân tích cả ngữ cảnh chat
- Xác định rõ lý do chọn agent
- Ưu tiên CustomerServiceAgent cho các câu hỏi về khiếu nại/phàn nàn
- Ưu tiên AnalyticsAgent cho các câu hỏi về đánh giá/phân tích
- Ưu tiên ProductManagementAgent cho các câu hỏi về quản lý sản phẩm"""

            # Get analysis from LLM
            analysis = await self._get_llm_analysis(prompt)
            
            # Parse and validate analysis
            try:
                result = json.loads(analysis)
                if not isinstance(result, dict) or 'agents' not in result:
                    raise ValueError("Invalid analysis format")
                
                # Kiểm tra và điều chỉnh agent cho câu hỏi về khiếu nại
                if any(keyword in message.lower() for keyword in ["phàn nàn", "kêu", "báo lỗi", "kém chất lượng"]):
                    # Tìm CustomerServiceAgent trong danh sách
                    customer_service_agent = next(
                        (agent for agent in result["agents"] if agent["agent"] == "CustomerServiceAgent"),
                        None
                    )
                    
                    if customer_service_agent:
                        # Tăng độ tin cậy cho CustomerServiceAgent
                        customer_service_agent["confidence"] = 0.9
                        customer_service_agent["intent"] = "handle_complaint"
                        customer_service_agent["reason"] = "Câu hỏi liên quan đến khiếu nại/phàn nàn của khách hàng"
                    else:
                        # Thêm CustomerServiceAgent nếu chưa có
                        result["agents"].append({
                            "agent": "CustomerServiceAgent",
                            "reason": "Câu hỏi liên quan đến khiếu nại/phàn nàn của khách hàng",
                            "confidence": 0.9,
                            "keywords": ["phàn nàn", "kém chất lượng", "khiếu nại"],
                            "intent": "handle_complaint"
                        })
                    
                    # Cập nhật primary_intent
                    result["primary_intent"] = "handle_complaint"
                
                return result
                
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    if not isinstance(result, dict) or 'agents' not in result:
                        raise ValueError("Invalid analysis format")
                    return result
                raise ValueError("Could not parse analysis as JSON")
                
        except Exception as e:
            logger.error(f"Error in _analyze_message_for_agents: {str(e)}")
            # Return default analysis with CustomerServiceAgent for complaints
            if any(keyword in message.lower() for keyword in ["phàn nàn", "kêu", "báo lỗi", "kém chất lượng"]):
                return {
                    "agents": [{
                        "agent": "CustomerServiceAgent",
                        "reason": "Câu hỏi liên quan đến khiếu nại/phàn nàn của khách hàng",
                        "confidence": 0.9,
                        "keywords": ["phàn nàn", "kém chất lượng", "khiếu nại"],
                        "intent": "handle_complaint"
                    }],
                    "requires_multiple_agents": False,
                    "primary_intent": "handle_complaint",
                    "secondary_intents": []
                }
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
            if agent_name == "ProductManagementAgent":
                return await self.product_mgmt.process(request)
            elif agent_name == "InventoryAgent":
                result = await self.inventory.process(request)
                if not result:
                    return {
                        "message": "❌ Không thể lấy thông tin tồn kho. Vui lòng thử lại sau.",
                        "type": "error"
                    }
                return {
                    "message": result.get("message", ""),
                    "type": result.get("type", "text"),
                    "data": {
                        "inventory": result.get("inventory", []),
                        "total_items": result.get("total_items", 0),
                        "total_value": result.get("total_value", 0),
                        "low_stock_items": result.get("low_stock_items", [])
                    }
                }
            elif agent_name == "MarketingAgent":
                result = await self.marketing.process(request)
                if not result:
                    return {
                        "message": "❌ Không thể xử lý yêu cầu marketing. Vui lòng thử lại sau.",
                        "type": "error"
                    }
                return {
                    "message": result.get("message", ""),
                    "type": result.get("type", "text"),
                    "data": {
                        "campaigns": result.get("campaigns", []),
                        "promotions": result.get("promotions", []),
                        "total_campaigns": result.get("total_campaigns", 0),
                        "active_promotions": result.get("active_promotions", 0)
                    }
                }
            elif agent_name == "CustomerServiceAgent":
                result = await self.customer_service.process(request)
                if not result:
                    return {
                        "message": "❌ Không thể xử lý yêu cầu chăm sóc khách hàng. Vui lòng thử lại sau.",
                        "type": "error"
                    }
                return {
                    "message": result.get("message", ""),
                    "type": result.get("type", "text"),
                    "data": {
                        "tickets": result.get("tickets", []),
                        "reviews": result.get("reviews", []),
                        "total_tickets": result.get("total_tickets", 0),
                        "total_reviews": result.get("total_reviews", 0),
                        "average_rating": result.get("average_rating", 0)
                    }
                }
            elif agent_name == "AnalyticsAgent":
                result = await self.analytics.process(request)
                if not result:
                    return {
                        "message": "❌ Không thể lấy thông tin phân tích. Vui lòng thử lại sau.",
                        "type": "error"
                    }
                return {
                    "message": result.get("message", ""),
                    "type": result.get("type", "text"),
                    "data": {
                        "revenue": result.get("revenue", 0),
                        "orders": result.get("orders", 0),
                        "customers": result.get("customers", 0),
                        "products": result.get("products", []),
                        "inventory": result.get("inventory", []),
                        "metrics": result.get("metrics", {})
                    }
                }
            else:
                return {
                    "message": "❌ Xin lỗi, tôi không hiểu yêu cầu của bạn. Bạn có thể thử lại không?",
                    "type": "error",
                    "data": {}
                }
        except Exception as e:
            logger.error(f"Error processing with agent {agent_name}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "message": f"❌ Đã có lỗi xảy ra khi xử lý yêu cầu: {str(e)}",
                "type": "error",
                "data": {}
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

    async def process_request(self, request: ShopRequest) -> Dict[str, Any]:
        """Process a shop management request"""
        try:
            # Route to appropriate handler based on request type
            if "inventory" in request.message.lower():
                return await self.inventory.process_request(request.dict())
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