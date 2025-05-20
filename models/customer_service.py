from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import ForeignKey, String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class CustomerService(Base, TimestampMixin):
    __tablename__ = "customer_service"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    ticket_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, in_progress, resolved, closed
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")  # low, medium, high, urgent
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # product, order, payment, technical, other
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.customer_id"), nullable=True)
    response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in minutes
    resolution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in minutes
    ticket_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional data like attachments, tags, etc.
    
    # Relationships
    shop = relationship("Shop", back_populates="customer_service_tickets")
    customer = relationship("Customer", back_populates="service_tickets", foreign_keys=[customer_id])
    assignee = relationship("Customer", back_populates="assigned_tickets", foreign_keys=[assigned_to])


class CustomerServiceCreate(BaseModel):
    shop_id: int
    customer_id: int
    subject: str
    description: str
    category: str
    priority: str = "medium"
    assigned_to: Optional[int] = None
    ticket_metadata: Optional[Dict[str, Any]] = None


class CustomerServiceUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    response_time: Optional[float] = None
    resolution_time: Optional[float] = None
    ticket_metadata: Optional[Dict[str, Any]] = None


class CustomerServiceResponse(BaseModel):
    id: int
    shop_id: int
    customer_id: int
    ticket_id: str
    subject: str
    description: str
    status: str
    priority: str
    category: str
    assigned_to: Optional[int]
    response_time: Optional[float]
    resolution_time: Optional[float]
    ticket_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 