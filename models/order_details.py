from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class OrderDetail(Base):
    __tablename__ = "order_details"
    
    order_detail_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    discount: Mapped[float] = mapped_column(DECIMAL, nullable=False, default=0)
    
    # Relationships
    order = relationship("Order", back_populates="details")
    product = relationship("Product", back_populates="order_details")

class OrderDetailCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: float
    discount: float = 0
    
    class Config:
        from_attributes = True

class OrderDetailUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None
    discount: Optional[float] = None
    
    class Config:
        from_attributes = True

class OrderDetailModel(BaseModel):
    detail_id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    discount: float
    
    class Config:
        from_attributes = True
