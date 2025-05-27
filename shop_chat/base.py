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
    system_message="""Bạn là một trợ lý AI thông minh làm việc cho sàn thương mại điện tử IUH-Ecomerce
    Bạn sẽ nhận đầu vào câu hỏi của người bán hàng về quản lý shop trên sàn
    Nhiệm vụ của bạn là trả lời câu hỏi và hỗ trợ người bán một cách chính xác và đầy đủ nhất có thể
    Nếu bạn chưa đủ thông tin trả lời, bạn hãy sử dụng các trợ lý khác để tìm kiếm thông tin
    Hãy trả về mô tả truy vấn dưới dạng JSON:
    {
        "agent": "ProductManagementAgent" | "InventoryAgent" | "OrderAgent" | "MarketingAgent" | "AnalyticsAgent" | "FinanceAgent" | "PolicyAgent" | "CustomerServiceAgent",
        "query": String
    }
    Với Agent là tên của trợ lý mà bạn muốn sử dụng để tìm kiếm thông tin:
        ProductManagementAgent: Quản lý sản phẩm (đăng, cập nhật, xóa)
        InventoryAgent: Quản lý tồn kho
        OrderAgent: Xử lý đơn hàng
        MarketingAgent: Quản lý khuyến mãi và marketing
        AnalyticsAgent: Phân tích và báo cáo
        FinanceAgent: Quản lý tài chính và thanh toán
        PolicyAgent: Hỗ trợ chính sách và quy định
        CustomerServiceAgent: Quản lý tương tác khách hàng

    Kết quả là 1 json duy nhất, không có văn bản mô tả nào khác ngoài json này.
    {
        "agent": "ProductManagementAgent" | "InventoryAgent" | "OrderAgent" | "MarketingAgent" | "AnalyticsAgent" | "FinanceAgent" | "PolicyAgent" | "CustomerServiceAgent",
        "query": String
    }
    """,
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
)

async def process_shop_chat(request: ShopRequest) -> Dict[str, Any]:
    try:
        # Get response from ShopManager
        print(f"✅🙌❎🤷‍♂️🤦‍♀️🤦‍♀️{request.mesage}")
        chat = await ShopManager.a_generate_reply(
            messages=[{"role": "user", "content": request.message}]
        )
        logger.info(f"Raw ShopManager response: {chat}")
        logger.info(f"Response type: {type(chat)}")
        
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
                            "agent": "ProductManagementAgent",
                            "query": request.message
                        }
                else:
                    parsed_content = {
                        "agent": "ProductManagementAgent",
                        "query": request.message
                    }
        else:
            logger.warning(f"Unexpected response type: {type(chat)}")
            parsed_content = {
                "agent": "ProductManagementAgent",
                "query": request.message
            }
        
        logger.info(f"Parsed content: {parsed_content}")
        
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
            from sqlalchemy.orm import Session
            from db import SessionLocal
            
            # Create a new database session
            db = SessionLocal()
            try:
                agent = MarketingAgent(shop_id=request.shop_id, db=db)
                result = await agent.process(request)
                
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
            
        # Add other agent types here as needed
        
    except Exception as e:
        logger.error(f"Error processing shop chat: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Fallback to direct content if not JSON or parsing fails
        return {
            "agent": "ShopManager",
            "response": {
                "content": "Xin lỗi, tôi không thể xử lý yêu cầu của bạn. Vui lòng thử lại sau.",
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
