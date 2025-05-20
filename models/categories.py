from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Category(Base):
    __tablename__ = "categories"
    category_id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=True)
    path: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
    promotions: Mapped[List["Promotion"]] = relationship("Promotion", back_populates="category")

class CategoryCreate(BaseModel):
    category_id: str
    name: str
    path: str

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CategoryResponse(BaseModel):
    category_id: str
    name: str
    path: str

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True