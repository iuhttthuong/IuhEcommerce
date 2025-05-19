from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
import enum
from models.base import Base, TimestampMixin

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    shipping_address: Mapped[str] = mapped_column(String, nullable=False)
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    payment_status: Mapped[str] = mapped_column(String, nullable=False)
    tracking_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class OrderCreate(BaseModel):
    customer_id: int
    total_amount: float
    shipping_address: str
    payment_method: str
    payment_status: str
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    payment_status: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    total_amount: float
    status: OrderStatus
    shipping_address: str
    payment_method: str
    payment_status: str
    tracking_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 