from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
import sqlalchemy as sa
from models.base import Base, TimestampMixin
from models.shops import Shop

class ShopChatSession(Base, TimestampMixin):
    __tablename__ = "shop_chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    agent: Mapped[str] = mapped_column(String(50), nullable=False)
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    # Relationships
    shop = relationship("Shop", back_populates="chat_sessions")
    messages = relationship("ShopChatMessage", back_populates="session", cascade="all, delete-orphan")

class ShopChatMessage(Base, TimestampMixin):
    __tablename__ = "shop_chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("shop_chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)

    # Relationships
    session = relationship("ShopChatSession", back_populates="messages")

# Pydantic models for API
class ShopChatSessionCreate(BaseModel):
    shop_id: int
    agent: str
    context: Optional[Dict[str, Any]] = None

class ShopChatSessionModel(BaseModel):
    id: int
    shop_id: int
    agent: str
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShopChatMessageCreate(BaseModel):
    session_id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None

class ShopChatMessageModel(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ShopChatHistoryResponse(BaseModel):
    session: ShopChatSessionModel
    messages: List[ShopChatMessageModel]

    class Config:
        from_attributes = True 