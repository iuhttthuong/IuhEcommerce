from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductVariant(Base, TimestampMixin):
    __tablename__ = "product_variants"
    
    variant_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    attributes: Mapped[Dict] = mapped_column(JSON, nullable=False)  # e.g., {"color": "red", "size": "XL"}
    is_active: Mapped[bool] = mapped_column(default=True)

class ProductVariantCreate(BaseModel):
    product_id: int
    sku: str
    price: float
    stock: int
    attributes: Dict
    is_active: bool = True

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    attributes: Optional[Dict] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductVariantResponse(BaseModel):
    variant_id: int
    product_id: int
    sku: str
    price: float
    stock: int
    attributes: Dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 