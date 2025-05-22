from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from typing import List
from models.base import Base, TimestampMixin
from models.cart_items import CartItem

class ShoppingCart(Base, TimestampMixin):
    __tablename__ = "shopping_carts"
    cart_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)

    items: Mapped[List["CartItem"]] = relationship("CartItem", backref="cart", cascade="all, delete-orphan")

class ShoppingCartCreate(BaseModel):
    customer_id: int

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ShoppingCartModel(BaseModel):
    cart_id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
    
    