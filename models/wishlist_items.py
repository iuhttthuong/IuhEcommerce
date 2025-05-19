from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class WishlistItem(Base, TimestampMixin):
    __tablename__ = "wishlist_items"
    
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.wishlist_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    priority: Mapped[int] = mapped_column(default=0)  # Higher number means higher priority
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)  # For price drop notifications
    item_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class WishlistItemCreate(BaseModel):
    wishlist_id: int
    product_id: int
    quantity: int = 1
    notes: Optional[str] = None
    priority: int = 0
    item_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class WishlistItemUpdate(BaseModel):
    quantity: Optional[int] = None
    notes: Optional[str] = None
    priority: Optional[int] = None
    is_notified: Optional[bool] = None
    item_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class WishlistItemResponse(BaseModel):
    item_id: int
    wishlist_id: int
    product_id: int
    quantity: int
    notes: Optional[str]
    priority: int
    is_notified: bool
    item_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 