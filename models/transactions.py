from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, DECIMAL, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
import enum
from models.base import Base, TimestampMixin

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    REFUND = "refund"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    
    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    amount: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="VND")
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    payment_method: Mapped[str] = mapped_column(String, nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    transaction_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class TransactionCreate(BaseModel):
    user_id: int
    amount: float
    currency: str = "VND"
    status: TransactionStatus
    type: TransactionType
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    description: Optional[str] = None
    transaction_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    description: Optional[str] = None
    transaction_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: int
    amount: float
    currency: str
    status: TransactionStatus
    type: TransactionType
    payment_method: Optional[str]
    payment_id: Optional[str]
    description: Optional[str]
    transaction_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 