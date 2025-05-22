from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
import enum
from models.base import Base
# from models.order_items import OrderItem
from models.products import Product

class Order(Base):
    __tablename__ = "orders"
    
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    order_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    delivery_method: Mapped[str] = mapped_column(String, nullable=False)
    delivery_fee: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    discount_amount: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    transaction_code: Mapped[str] = mapped_column(String, nullable=False)
    
    # Relationships
    # details = relationship("OrderDetail", back_populates="order")
    # customer = relationship("Customer", back_populates="orders")

class OrderCreate(BaseModel):
    customer_id: int
    total_amount: float
    payment_method: str
    delivery_method: str
    delivery_fee: float
    discount_amount: float
    transaction_code: str
    class config:
        from_attributes = True

class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    delivery_method: Optional[str] = None
    delivery_fee: Optional[float] = None
    discount_amount: Optional[float] = None
    transaction_code: Optional[str] = None
    class config:
        from_attributes = True

class OrderModel(BaseModel):
    order_id: int
    customer_id: int
    total_amount: float
    order_date: datetime
    payment_method: str
    delivery_method: str
    delivery_fee: float
    discount_amount: float
    transaction_code: str
    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
        
        
class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    total_amount: float
    order_date: datetime
    payment_method: str
    delivery_method: str
    delivery_fee: float
    discount_amount: float
    transaction_code: str
    
    class Config:
        from_attributes = True

    