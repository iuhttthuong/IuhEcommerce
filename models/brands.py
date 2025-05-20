from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Brand(Base):
    __tablename__ = "brands"
    brand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    brand_name: Mapped[str] = mapped_column(nullable=False)
    brand_slug: Mapped[str] = mapped_column(nullable=True)
    brand_country: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand")

class BrandCreate(BaseModel):
    brand_id: int
    brand_name: str
    brand_slug: str
    brand_country: str
    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class BrandResponse(BaseModel):
    brand_id: int
    brand_name: str
    brand_slug: str
    brand_country: str

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True