from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import ForeignKey, TIMESTAMP, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductSpecification(Base, TimestampMixin):
    __tablename__ = "product_specifications"
    
    specification_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "General", "Technical", "Warranty"
    specifications: Mapped[Dict] = mapped_column(JSON, nullable=False)  # e.g., {"Screen": "6.1 inch", "Battery": "4000mAh"}
    display_order: Mapped[int] = mapped_column(default=0)

class ProductSpecificationCreate(BaseModel):
    product_id: int
    category: str
    specifications: Dict
    display_order: int = 0

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductSpecificationUpdate(BaseModel):
    category: Optional[str] = None
    specifications: Optional[Dict] = None
    display_order: Optional[int] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductSpecificationResponse(BaseModel):
    specification_id: int
    product_id: int
    category: str
    specifications: Dict
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 