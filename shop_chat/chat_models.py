from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: Optional[int] = None
    chat_id: int
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ShopChatSession(BaseModel):
    id: Optional[int] = None
    shop_id: int
    user_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = "active"
    context: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChatHistory(BaseModel):
    session: ShopChatSession
    messages: List[ChatMessage]

class ChatSummary(BaseModel):
    session_id: int
    shop_id: int
    user_id: Optional[int]
    message_count: int
    last_message: datetime
    topics: List[str]
    sentiment: Optional[str] = None

class ChatAnalytics(BaseModel):
    total_sessions: int
    active_sessions: int
    average_messages_per_session: float
    common_topics: List[Dict[str, Any]]
    average_response_time: float
    satisfaction_score: Optional[float] = None
    peak_hours: Dict[str, int] 