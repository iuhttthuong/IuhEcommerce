from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"
    
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("shopping_carts.cart_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    selected: Mapped[bool] = mapped_column(Boolean, default=True)
    item_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = 1
    selected: bool = True
    item_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    selected: Optional[bool] = None
    item_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CartItemResponse(BaseModel):
    item_id: int
    cart_id: int
    product_id: int
    quantity: int
    selected: bool
    item_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 