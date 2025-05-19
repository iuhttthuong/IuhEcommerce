from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=True)
    product_short_url: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    short_description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL, nullable=True)
    original_price: Mapped[float] = mapped_column(DECIMAL, nullable=True)
    discount: Mapped[float] = mapped_column(DECIMAL, nullable=True)
    discount_rate: Mapped[int] = mapped_column(nullable=True)
    sku: Mapped[str] = mapped_column(nullable=True)
    review_text: Mapped[str] = mapped_column(nullable=True)
    quantity_sold: Mapped[int] = mapped_column(nullable=True)
    rating_average: Mapped[float] = mapped_column(DECIMAL, nullable=True)
    review_count: Mapped[int] = mapped_column(nullable=True)
    order_count: Mapped[int] = mapped_column(nullable=True)
    favourite_count: Mapped[int] = mapped_column(nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(nullable=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.category_id"), nullable=False) 
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.brand_id"), nullable=False) 
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.seller_id"), nullable=False) 
    shippable: Mapped[bool] = mapped_column(nullable=True)
    availability: Mapped[bool] = mapped_column(nullable=True)

class ProductCreate(BaseModel):
    product_id: int
    name: str
    product_short_url: str
    description: str
    short_description: str
    price: float
    original_price: float
    discount: float
    discount_rate: int
    sku: str
    review_text: str
    quantity_sold: int
    rating_average: float
    review_count: int
    order_count: int
    favourite_count: int
    thumbnail_url: str
    category_id: str
    brand_id: int
    seller_id: int
    shippable: bool
    availability: bool

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductModel(BaseModel):
    product_id: int
    name: str
    product_short_url: str
    description: str
    short_description: str
    price: float
    original_price: float
    discount: float
    discount_rate: int
    sku: str
    review_text: str
    quantity_sold: int
    rating_average: float
    review_count: int
    order_count: int
    favourite_count: int
    thumbnail_url: str
    category_id: str
    brand_id: int
    seller_id: int
    shippable: bool
    availability: bool

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductResponse(BaseModel):
    product_id: int
    name: str
    product_short_url: str
    description: str
    short_description: str
    price: float
    original_price: float
    discount: float
    discount_rate: int
    sku: str
    review_text: str
    quantity_sold: int
    rating_average: float
    review_count: int
    order_count: int
    favourite_count: int
    thumbnail_url: str
    category_id: str
    brand_id: Optional[int] = None
    seller_id: int
    shippable: bool
    availability: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True