from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ShoppingCart(Base, TimestampMixin):
    __tablename__ = "shopping_carts"
    
    cart_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cart_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class ShoppingCartCreate(BaseModel):
    user_id: int
    cart_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ShoppingCartUpdate(BaseModel):
    is_active: Optional[bool] = None
    cart_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ShoppingCartResponse(BaseModel):
    cart_id: int
    user_id: int
    is_active: bool
    cart_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 