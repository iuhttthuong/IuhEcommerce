from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Review(Base, TimestampMixin):
    __tablename__ = "reviews"
    
    review_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # List of image URLs
    likes: Mapped[int] = mapped_column(Integer, default=0)
    is_verified_purchase: Mapped[bool] = mapped_column(default=False)
    helpful_votes: Mapped[int] = mapped_column(Integer, default=0)
    review_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class ReviewCreate(BaseModel):
    user_id: int
    product_id: int
    rating: float
    title: Optional[str] = None
    content: str
    images: Optional[list] = None
    is_verified_purchase: bool = False
    review_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[list] = None
    review_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ReviewResponse(BaseModel):
    review_id: int
    user_id: int
    product_id: int
    rating: float
    title: Optional[str]
    content: str
    images: Optional[list]
    likes: int
    is_verified_purchase: bool
    helpful_votes: int
    review_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 