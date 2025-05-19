from typing import Optional
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from pydantic import BaseModel, Field
import sqlalchemy as sa
from models.chat import Chat

# SQLAlchemy base class
class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    chat_id: Mapped[int] = mapped_column( ForeignKey(Chat.id), nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    role: Mapped[str] = mapped_column(sa.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

# Payload khi tạo tin nhắn mới
class CreateMessagePayload(BaseModel):
    chat_id: int
    content: str
    role: str

# Model phản hồi trả về từ API
class MessageModel(BaseModel):
    id: int
    chat_id: int
    content: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UpdateMessagePayload(BaseModel):
    content: Optional[str]
    role: Optional[str]


