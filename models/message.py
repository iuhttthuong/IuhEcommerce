from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from models.chats import ChatMessage

# Model phản hồi trả về từ API
class MessageModel(BaseModel):
    message_id: int
    chat_id: int
    sender_type: str
    sender_id: str
    content: str
    is_read: bool
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
