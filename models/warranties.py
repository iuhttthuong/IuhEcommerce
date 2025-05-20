from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Warranty(Base):
    __tablename__ = "warranties"
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    warranty_location: Mapped[str] = mapped_column(nullable=False)
    warranty_period: Mapped[str] = mapped_column(nullable=False)
    warranty_form: Mapped[str] = mapped_column(nullable=False)
    warranty_url: Mapped[str] = mapped_column(nullable=False)
    return_policy: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="warranties")

class WarrantyCreate(BaseModel):
    product_id: int
    warranty_location: str
    warranty_period: str
    warranty_form: str
    warranty_url: str
    return_policy: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class WarrantyResponse(BaseModel):
    product_id: int
    warranty_location: str
    warranty_period: str
    warranty_form: str
    warranty_url: str
    return_policy: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True