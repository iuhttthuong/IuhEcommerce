from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"
    
    chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.customer_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")  # active, closed
    last_message_at: Mapped[datetime] = mapped_column(nullable=False)
    
    # Relationships
    shop = relationship("Shop", back_populates="chat_sessions")
    customer = relationship("Customer", back_populates="chats")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="chat")


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"
    
    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.chat_id"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)  # shop, customer
    sender_id: Mapped[int] = mapped_column(nullable=False)  # shop_id or customer_id
    content: Mapped[str] = mapped_column(nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")


class ChatCreate(BaseModel):
    shop_id: int
    customer_id: Optional[int] = None


class ChatMessageCreate(BaseModel):
    chat_id: int
    sender_type: str
    sender_id: int
    content: str


class UpdateMessagePayload(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None


class ChatResponse(BaseModel):
    chat_id: int
    shop_id: int
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
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 