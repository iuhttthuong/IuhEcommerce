from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from pydantic import BaseModel
import sqlalchemy as sa
from models.customers import Customer
class Base(DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column( primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(nullable=False, autoincrement=True, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(Customer.customer_id), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

class ChatCreate(BaseModel):
    user_id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
class ChatModel(BaseModel):
    id: int
    session_id: int
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
    session_id: int = None
    user_id: int = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True