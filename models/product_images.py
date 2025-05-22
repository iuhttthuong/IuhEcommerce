from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

    
class ProductImage(Base):
    __tablename__ = "product_images"
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    base_url: Mapped[str] = mapped_column(nullable=False)
    large_url: Mapped[str] = mapped_column(nullable=False)
    medium_url: Mapped[str] = mapped_column(nullable=False)
    is_gallery: Mapped[bool] = mapped_column(nullable=True)


class ProductImageCreate(BaseModel):
    product_id: int
    base_url: str
    large_url: str
    medium_url: str
    is_gallery: Optional[bool] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True


class ProductImageResponse(BaseModel):
    product_id: int
    base_url: str
    large_url: str
    medium_url: str
    is_gallery: Optional[bool] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True