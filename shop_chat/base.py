from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json
from autogen import AssistantAgent, ConversableAgent
from env import env
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session
import traceback
import logging

logging.basicConfig(
    level=logging.INFO,  # hoặc DEBUG nếu muốn ghi chi tiết
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),  # Ghi vào file
        logging.StreamHandler(),  # Đồng thời in ra console
    ],
)

logger = logging.getLogger(__name__)


# Base configuration for shop agents
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": env.OPENAI_API_KEY
    }
]

class ShopAgentRequest(BaseModel):
    shop_id: int 
    message: str
    context: str

class ShopAgentResponse(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = None

class AgentMessage(BaseModel):
    agent_id: str
    agent_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ShopRequest(BaseModel):
    message: str
    chat_id: int
    shop_id: Optional[int] = None
    user_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    entities: Optional[Dict[str, Any]] = None
    agent_messages: Optional[List[AgentMessage]] = None
    filters: Optional[Dict[str, Any]] = None

class ChatMessageRequest(BaseModel):
    chat_id: int
    sender_type: str
    sender_id: int
    content: str
    message_metadata: Optional[Dict[str, Any]] = None

class BaseShopAgent(ABC):
    def __init__(self, shop_id: int = None, name: str = None, system_message: str = None):
        self.shop_id = shop_id
        self.name = name or self.__class__.__name__
        self.system_message = system_message
        self.assistant = AssistantAgent(
            name=self.name,
            system_message=self.system_message or """Bạn là một trợ lý AI thông minh làm việc cho sàn thương mại điện tử IUH-Ecomerce\nBạn sẽ nhận đầu vào câu hỏi của người bán hàng về quản lý shop trên sàn\nNhiệm vụ của bạn là trả lời câu hỏi và hỗ trợ người bán một cách chính xác và đầy đủ nhất có thể\nNếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin\nHãy trả về mô tả truy vấn dưới dạng JSON:\n{\n    \"agent\": \"ProductManagementAgent\" | \"InventoryAgent\" | \"OrderAgent\" | \"MarketingAgent\" | \"AnalyticsAgent\" | \"FinanceAgent\" | \"PolicyAgent\" | \"CustomerServiceAgent\",\n    \"query\": String\n}\nVới Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin:\n    ProductManagementAgent: Quản lý sản phẩm (đăng, cập nhật, xóa)\n    InventoryAgent: Quản lý tồn kho\n    OrderAgent: Xử lý đơn hàng\n    MarketingAgent: Quản lý khuyến mãi và marketing\n    AnalyticsAgent: Phân tích và báo cáo\n    FinanceAgent: Quản lý tài chính và thanh toán\n    PolicyAgent: Hỗ trợ chính sách và quy định\n    CustomerServiceAgent: Quản lý tương tác khách hàng\n""",
            llm_config={"config_list": config_list},
            max_consecutive_auto_reply=2
        )
        self.message_repository = None  # Will be set by child classes

    @abstractmethod
    async def process(self, request: ShopRequest) -> Dict[str, Any]:
        pass

    def _create_response(self, response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "response": {
                "title": self._get_response_title(response),
                "content": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.name,
            "context": {
                "search_results": [],
                "shop_id": self.shop_id
            },
            "timestamp": datetime.now().isoformat()
        }

    def _get_response_title(self, query: str) -> str:
        """Get the title for the response. Override in child classes."""
        return "Câu trả lời từ trợ lý AI"

    def _get_fallback_response(self) -> str:
        """Get the fallback response when no results are found. Override in child classes."""
        return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn. Vui lòng thử lại sau hoặc liên hệ bộ phận hỗ trợ shop."

    def _get_error_response(self) -> Dict[str, Any]:
        """Get the error response. Override in child classes."""
        return {
            "response": {
                "title": "Lỗi xử lý yêu cầu",
                "content": self._get_fallback_response(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "agent": self.name,
            "context": {},
            "timestamp": datetime.now().isoformat()
        }

# Base shop agent configuration
ShopManager = ConversableAgent(
    name="shop_manager",
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho sàn thương mại điện tử IUH-Ecomerce.
    Bạn sẽ nhận đầu vào câu hỏi của người bán hàng về quản lý shop trên sàn.
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
       - "Sản phẩm kém chất lượng..."
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
    human_input_mode="NEVER",
)

async def process_shop_chat(request: ShopRequest) -> Dict[str, Any]:
    try:
        # Get response from ShopManager
        print(f"✅🙌❎🤷‍♂️🤦‍♀️🤦‍♀️{request.message}")
        chat = await ShopManager.a_generate_reply(
            messages=[{"role": "user", "content": request.message}]
        )
        logger.info(f"Raw ShopManager response: {chat}")
        logger.info(f"Response type: {type(chat)}")
        print(f"angent phản hồi: {chat}")
        # Handle the response content
        parsed_content = None

        if isinstance(chat, dict):
            logger.info("Response is a dictionary")
            parsed_content = chat
        elif isinstance(chat, str):
            logger.info("Response is a string")
            try:
                # First try direct JSON parsing
                parsed_content = json.loads(chat)
                logger.info("Successfully parsed JSON from string")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {str(e)}")
                # If that fails, try to extract JSON from markdown code block
                if chat.startswith("```json") and chat.endswith("```"):
                    json_str = chat.replace("```json", "").replace("```", "").strip()
                    try:
                        parsed_content = json.loads(json_str)
                        logger.info("Successfully parsed JSON from markdown block")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from markdown: {str(e)}")
                        parsed_content = {
                            "agent": "AnalyticsAgent" if "đánh giá" in request.message.lower() else "PolicyAgent" if "chính sách" in request.message.lower() else "ProductManagementAgent",
                            "query": request.message
                        }
                else:
                    parsed_content = {
                        "agent": "AnalyticsAgent" if "đánh giá" in request.message.lower() else "PolicyAgent" if "chính sách" in request.message.lower() else "ProductManagementAgent",
                        "query": request.message
                    }
        else:
            logger.warning(f"Unexpected response type: {type(chat)}")
            parsed_content = {
                "agent": "AnalyticsAgent" if "đánh giá" in request.message.lower() else "PolicyAgent" if "chính sách" in request.message.lower() else "ProductManagementAgent",
                "query": request.message
            }

        logger.info(f"Parsed content: {parsed_content}")
        print(f"parsed content: {parsed_content}")
        # Extract agent and query from the parsed content
        agent_type = parsed_content.get("agent")
        query = parsed_content.get("query")

        if not agent_type or not query:
            logger.error("Missing agent or query in response")
            raise ValueError("Missing agent or query in response")

        # Route to appropriate agent based on agent type
        if agent_type == "ProductManagementAgent":
            from shop_chat.product_management import ProductManagement
            from sqlalchemy.orm import Session
            from db import SessionLocal

            # Create a new database session
            db = SessionLocal()
            try:
                agent = ProductManagement(db)
                result = await agent.process({
                    "message": query,
                    "shop_id": request.shop_id,
                    "chat_history": request.context.get("chat_history", "")
                })

                # Ensure the response content is a string
                response_content = result.get('message', '')
                if response_content is None:
                    response_content = "Không có phản hồi từ hệ thống."
                elif not isinstance(response_content, str):
                    response_content = str(response_content)

                # Format the response according to the expected structure
                return {
                    "agent": agent_type,
                    "response": {
                        "content": response_content,
                        "type": result.get('type', 'text')
                    },
                    "timestamp": datetime.now().isoformat(),
                    "chat_id": request.chat_id
                }
            finally:
                db.close()

        elif agent_type == "MarketingAgent":
            from shop_chat.marketing import MarketingAgent
            from db import SessionLocal
            print("❎❎ agne tmarrketing dược chọn")
            # Create a new database session
            db = SessionLocal()
            try:
                agent = MarketingAgent(shop_id=request.shop_id)
                print(f"🙌🙌🙌🛒🛒🛒🛒request: {request}")
                result = await agent.process(request)
                # print(f"🧠✅❎❎💣 kết quả của agent makerting: {result}")
                # Ensure the response content is a string
                response_content = result.get('message', '')
                if response_content is None:
                    response_content = "Không có phản hồi từ hệ thống."
                elif not isinstance(response_content, str):
                    response_content = str(response_content)
                
                return {
                    "agent": agent_type,
                    "response": {
                        "content": response_content,
                        "type": result.get('type', 'text')
                    },
                    "timestamp": datetime.now().isoformat(),
                    "chat_id": request.chat_id
                }
            finally:
                db.close()

        elif agent_type == "AnalyticsAgent":
            from shop_chat.analytics import Analytics
            from sqlalchemy.orm import Session
            from db import SessionLocal

            # Create a new database session
            db = SessionLocal()
            try:
                agent = Analytics(db, shop_id=request.shop_id)
                result = await agent.process({
                    "message": query,
                    "shop_id": request.shop_id,
                    "chat_history": request.context.get("chat_history", "")
                })

                # Ensure the response content is a string
                response_content = result.get('message', '')
                if response_content is None:
                    response_content = "Không có phản hồi từ hệ thống."
                elif not isinstance(response_content, str):
                    response_content = str(response_content)

                return {
                    "agent": agent_type,
                    "response": {
                        "content": response_content,
                        "type": result.get('type', 'text')
                    },
                    "timestamp": datetime.now().isoformat(),
                    "chat_id": request.chat_id
                }
            finally:
                db.close()

        elif agent_type == "PolicyAgent":
            from shop_chat.policy import PolicyAgent
            from sqlalchemy.orm import Session
            from db import SessionLocal

            # Create a new database session
            db = SessionLocal()
            try:
                agent = PolicyAgent(shop_id=request.shop_id, db=db)
                result = await agent.process({
                    "message": query,
                    "shop_id": request.shop_id,
                    "chat_history": request.context.get("chat_history", "")
                })

                # Ensure the response content is a string
                response_content = result.get('message', '')
                if response_content is None:
                    response_content = "Không có phản hồi từ hệ thống."
                elif not isinstance(response_content, str):
                    response_content = str(response_content)

                return {
                    "agent": agent_type,
                    "response": {
                        "content": response_content,
                        "type": result.get('type', 'text')
                    },
                    "timestamp": datetime.now().isoformat(),
                    "chat_id": request.chat_id
                }
            finally:
                db.close()

        else:
            # Default to ProductManagementAgent if agent type is not recognized
            from shop_chat.product_management import ProductManagement
            from sqlalchemy.orm import Session
            from db import SessionLocal

            # Create a new database session
            db = SessionLocal()
            try:
                agent = ProductManagement(db)
                result = await agent.process({
                    "message": query,
                    "shop_id": request.shop_id,
                    "chat_history": request.context.get("chat_history", "")
                })

                # Ensure the response content is a string
                response_content = result.get('message', '')
                if response_content is None:
                    response_content = "Không có phản hồi từ hệ thống."
                elif not isinstance(response_content, str):
                    response_content = str(response_content)

                return {
                    "agent": "ProductManagementAgent",
                    "response": {
                        "content": response_content,
                        "type": result.get('type', 'text')
                    },
                    "timestamp": datetime.now().isoformat(),
                    "chat_id": request.chat_id
                }
            finally:
                db.close()

    except Exception as e:
        logger.error(f"Error in process_shop_chat: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "agent": "System",
            "response": {
                "content": "Đã có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại sau.",
                "type": "error"
            },
            "timestamp": datetime.now().isoformat(),
            "chat_id": request.chat_id
        }

async def get_shop_info(query):
    chat = await ShopManager.a_generate_reply(
        messages=[{"role": "user", "content": query}])
    print(f"Chat: {chat}")
    content = chat.get("content", "")
    
    # Extract JSON from markdown code block if present
    if content.startswith("```json") and content.endswith("```"):
        try:
            json_str = content.replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    return {"content": content} 
