from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Wishlist(Base, TimestampMixin):
    __tablename__ = "wishlists"
    
    wishlist_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    wishlist_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class WishlistCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    is_public: bool = False
    is_default: bool = False
    wishlist_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class WishlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_default: Optional[bool] = None
    wishlist_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class WishlistResponse(BaseModel):
    wishlist_id: int
    user_id: int
    name: str
    description: Optional[str]
    is_public: bool
    is_default: bool
    wishlist_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 