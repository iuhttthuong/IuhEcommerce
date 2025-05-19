from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
import sqlalchemy as sa
from models.customers import Customer 
from models.shop import Shop
from models.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    message_metadata: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shops.seller_id"), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Customer.customer_id), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'customer' or 'shop'
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    context: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ChatCreate(BaseModel):
    shop_id: int
    user_id: int
    context: Optional[str] = None
    role: str  # 'customer' or 'shop'

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ChatModel(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UpdateChatPayload(BaseModel):
    user_id: int = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ChatHistoryResponse(BaseModel):
    session: ChatModel
    messages: List[ChatMessage]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True