from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class AgentMessage(BaseModel):
    agent_id: str
    agent_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent_id: str
    agent_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatbotRequest(BaseModel):
    chat_id: int
    message: str
    context: dict = None
    user_id: Optional[int] = None
    shop_id: Optional[int] = None
    entities: Optional[Dict[str, Any]] = None
    agent_messages: Optional[List[AgentMessage]] = None
    filters: Optional[Dict[str, Any]] = None 