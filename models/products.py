from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field
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

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products", lazy="select")
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products", lazy="select")
    shop: Mapped["Shop"] = relationship("Shop", back_populates="products", foreign_keys=[seller_id], primaryjoin="Product.seller_id == Shop.shop_id", overlaps="products,seller", lazy="select")
    seller: Mapped["Seller"] = relationship("Seller", back_populates="products", foreign_keys=[seller_id], primaryjoin="Product.seller_id == Seller.seller_id", overlaps="products,shop", lazy="select")
    order_details: Mapped[List["OrderDetail"]] = relationship("OrderDetail", back_populates="product", lazy="select")

    
class ProductBase(BaseModel):
    name: Optional[str] = None
    product_short_url: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount: Optional[float] = None
    discount_rate: Optional[int] = None
    sku: Optional[str] = None
    review_text: Optional[str] = None
    quantity_sold: Optional[int] = None
    rating_average: Optional[float] = None
    review_count: Optional[int] = None
    order_count: Optional[int] = None
    favourite_count: Optional[int] = None
    thumbnail_url: Optional[str] = None
    category_id: Optional[str] = None
    brand_id: Optional[int] = None
    seller_id: Optional[int] = None
    shippable: Optional[bool] = None
    availability: Optional[bool] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductCreate(ProductBase):
    product_id: int

class ProductUpdate(ProductBase):
    pass

class ProductModel(ProductBase):
    product_id: int

class ProductResponse(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True