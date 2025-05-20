from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
import enum
from models.base import Base, TimestampMixin


class TransactionType(str, enum.Enum):
    INCOME = "income"  # Thu nhập từ đơn hàng
    EXPENSE = "expense"  # Chi phí vận chuyển, hoa hồng, etc.
    REFUND = "refund"  # Hoàn tiền
    WITHDRAWAL = "withdrawal"  # Rút tiền
    DEPOSIT = "deposit"  # Nạp tiền


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Finance(Base, TimestampMixin):
    __tablename__ = "finance"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.order_id"))  # Optional: linked to specific order
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    description: Mapped[Optional[str]] = mapped_column(Text)
    transaction_date: Mapped[datetime] = mapped_column(nullable=False)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100))  # External reference ID (e.g., payment gateway)
    
    # Relationships
    shop = relationship("Shop", back_populates="finances")
    order = relationship("Order", back_populates="finances")


class FinanceCreate(BaseModel):
    shop_id: int
    order_id: Optional[int] = None
    type: TransactionType
    amount: float
    description: Optional[str] = None
    transaction_date: datetime
    reference_id: Optional[str] = None


class FinanceUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None
    reference_id: Optional[str] = None


class FinanceResponse(BaseModel):
    id: int
    shop_id: int
    order_id: Optional[int]
    type: TransactionType
    amount: float
    status: TransactionStatus
    description: Optional[str]
    transaction_date: datetime
    reference_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 