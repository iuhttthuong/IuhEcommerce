from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class CartItem(Base):
    __tablename__ = "cart_items"
    cart_id: Mapped[int] = mapped_column(ForeignKey("shopping_carts.cart_id"), primary_key=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    added_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True

class CartItemModel(BaseModel):
    cart_id: int
    product_id: int
    quantity: int
    added_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True