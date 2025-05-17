from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class Review(Base):
    __tablename__ = "reviews"
    review_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    review_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    likes: Mapped[int] = mapped_column(nullable=True)
    dislikes: Mapped[int] = mapped_column(nullable=True)

class ReviewCreatePayload(BaseModel):
    product_id: int
    customer_id: int
    rating: int
    comment: str
    review_date: datetime
    likes: int
    dislikes: int

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
class ReviewUpdatePayload(BaseModel):
    review_id: int
    product_id: int
    customer_id: int
    rating: int
    comment: str
    review_date: datetime
    likes: int
    dislikes: int

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
class ReviewDeletePayload(BaseModel):
    review_id: int

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True


class ReviewModel(BaseModel):
    review_id: int
    product_id: int
    customer_id: int
    rating: int
    comment: str
    review_date: datetime
    likes: int
    dislikes: int

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True