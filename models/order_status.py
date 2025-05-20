from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class OrderStatus(Base, TimestampMixin):
    __tablename__ = "order_status"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "pending", "processing", "shipped", "delivered", "cancelled"
    note: Mapped[Optional[str]] = mapped_column(Text)  # Optional note about the status change
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.customer_id"))  # Customer who updated the status
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
    customer = relationship("Customer", back_populates="order_status_updates")


class OrderStatusCreate(BaseModel):
    order_id: int
    status: str
    note: Optional[str] = None
    updated_by: Optional[int] = None


class OrderStatusUpdate(BaseModel):
    status: Optional[str] = None
    note: Optional[str] = None
    updated_by: Optional[int] = None


class OrderStatusResponse(BaseModel):
    id: int
    order_id: int
    status: str
    note: Optional[str]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 