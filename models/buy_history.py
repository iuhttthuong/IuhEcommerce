from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, DECIMAL, Integer
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class BuyHistory(Base, TimestampMixin):
    __tablename__ = "buy_history"
    
    history_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_time: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    total_amount: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    transaction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("transactions.transaction_id"), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "completed", "cancelled", "refunded"
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class BuyHistoryCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    price_at_time: float
    total_amount: float
    transaction_id: Optional[int] = None
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class BuyHistoryUpdate(BaseModel):
    quantity: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class BuyHistoryResponse(BaseModel):
    history_id: int
    user_id: int
    product_id: int
    quantity: int
    price_at_time: float
    total_amount: float
    transaction_id: Optional[int]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 