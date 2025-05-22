from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from pydantic import BaseModel, Field
from models.base import Base

class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.product_id"))
    customer_id: Mapped[int] = Column(Integer, ForeignKey("customers.customer_id"))
    rating: Mapped[int] = Column(Integer)
    comment: Mapped[str] = Column(Text)
    review_date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    likes: Mapped[int] = Column(Integer, default=0)
    dislikes: Mapped[int] = Column(Integer, default=0)

    # Define relationships
    customer = relationship("Customer", back_populates="reviews", lazy="joined")

class ReviewBase(BaseModel):
    product_id: int
    customer_id: int
    rating: int = Field(ge=1, le=5)
    comment: str

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    review_id: int
    review_date: datetime
    likes: int
    dislikes: int

    class Config:
        from_attributes = True

class ReviewDelete(BaseModel):
    review_id: int

    class Config:
        from_attributes = True

class ReviewLike(BaseModel):
    review_id: int
    customer_id: int

    class Config:
        from_attributes = True

class ReviewDislike(BaseModel):
    review_id: int
    customer_id: int

    class Config:
        from_attributes = True

class ReviewModel(BaseModel):
    review_id: int
    customer_id: int
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