from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
import enum
from models.base import Base, TimestampMixin


class ShippingMethod(str, enum.Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    SAME_DAY = "same_day"
    PICKUP = "pickup"


class ShippingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class Shipping(Base, TimestampMixin):
    __tablename__ = "shipping"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), nullable=False)
    method: Mapped[ShippingMethod] = mapped_column(Enum(ShippingMethod), nullable=False)
    status: Mapped[ShippingStatus] = mapped_column(Enum(ShippingStatus), nullable=False, default=ShippingStatus.PENDING)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    shipping_fee: Mapped[float] = mapped_column(nullable=False)
    estimated_delivery: Mapped[Optional[datetime]] = mapped_column()
    actual_delivery: Mapped[Optional[datetime]] = mapped_column()
    carrier: Mapped[Optional[str]] = mapped_column(String(100))  # Shipping company name
    address: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    order = relationship("Order", back_populates="shipping")


class ShippingCreate(BaseModel):
    order_id: int
    method: ShippingMethod
    shipping_fee: float
    address: str
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class ShippingUpdate(BaseModel):
    status: Optional[ShippingStatus] = None
    tracking_number: Optional[str] = None
    actual_delivery: Optional[datetime] = None
    carrier: Optional[str] = None
    notes: Optional[str] = None


class ShippingResponse(BaseModel):
    id: int
    order_id: int
    method: ShippingMethod
    status: ShippingStatus
    tracking_number: Optional[str]
    shipping_fee: float
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    carrier: Optional[str]
    address: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 