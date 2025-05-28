from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field
from models.base import Base, TimestampMixin


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"
    
    chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shops.shop_id"), nullable=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.customer_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")  # active, closed
    last_message_at: Mapped[datetime] = mapped_column(nullable=False)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    titles: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    # Relationships
    shop = relationship("Shop", back_populates="chat_sessions")
    customer = relationship("Customer", back_populates="chats")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
    

class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"
    
    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)  # shop, customer, agent, agent_response
    sender_id: Mapped[str] = mapped_column(String(36), nullable=False)  # shop_id, customer_id, or agent_id (UUID)
    content: Mapped[str] = mapped_column(nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False)
    message_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")


class ChatCreate(BaseModel):
    customer_id: Optional[int] = None
    shop_id: Optional[int] = None


class ChatMessageCreate(BaseModel):
    chat_id: int
    sender_type: str
    sender_id: Union[int, str]  # Can be either integer (for shop/customer) or string (for agent)
    content: str
    message_metadata: Optional[Dict[str, Any]] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Convert sender_id to string if it's an integer
        if isinstance(self.sender_id, int):
            self.sender_id = str(self.sender_id)


class UpdateMessagePayload(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None
    message_metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    chat_id: int
    shop_id: Optional[int] = None
    customer_id: Optional[int] = None
    status: str
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    message_id: int
    chat_id: int
    sender_type: str
    sender_id: str  # Always string in response
    content: str
    is_read: bool
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True