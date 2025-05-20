from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)  # Price at the time of order
    discount: Mapped[float] = mapped_column(default=0)    # Discount amount if any
    total: Mapped[float] = mapped_column(nullable=False)  # Total after discount
    notes: Mapped[Optional[str]] = mapped_column(String(255))  # Optional notes about the item
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: float
    discount: Optional[float] = 0
    notes: Optional[str] = None


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None
    discount: Optional[float] = None
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    discount: float
    total: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 