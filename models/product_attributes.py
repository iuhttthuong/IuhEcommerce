from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductAttribute(Base, TimestampMixin):
    __tablename__ = "product_attributes"
    
    attribute_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    display_order: Mapped[int] = mapped_column(default=0)

class ProductAttributeCreate(BaseModel):
    product_id: int
    name: str
    value: str
    unit: Optional[str] = None
    display_order: int = 0

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductAttributeUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    display_order: Optional[int] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductAttributeResponse(BaseModel):
    attribute_id: int
    product_id: int
    name: str
    value: str
    unit: Optional[str]
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 