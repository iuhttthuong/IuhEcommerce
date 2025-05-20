from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Seller(Base, TimestampMixin):
    __tablename__ = "sellers"
    seller_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    seller_name: Mapped[str] = mapped_column(nullable=False)
    seller_type: Mapped[str] = mapped_column(nullable=True)
    seller_link: Mapped[str] = mapped_column(nullable=True)
    seller_logo_url: Mapped[str] = mapped_column(nullable=True)
    seller_store_id: Mapped[int] = mapped_column(nullable=True)
    seller_is_best_store: Mapped[bool] = mapped_column(nullable=True)
    is_seller: Mapped[bool] = mapped_column(nullable=True)
    is_seller_in_chat_whitelist: Mapped[bool] = mapped_column(nullable=True)
    is_offline_installment_supported: Mapped[bool] = mapped_column(nullable=True)
    store_rating: Mapped[float] = mapped_column(DECIMAL, nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="seller")

class SellerCreate(BaseModel):
    seller_id: int
    seller_name: str
    seller_type: str
    seller_link: str
    seller_logo_url: str
    seller_store_id: int
    seller_is_best_store: bool
    is_seller: bool
    is_seller_in_chat_whitelist: bool
    is_offline_installment_supported: bool
    store_rating: float
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class SellerResponse(BaseModel):
    seller_id: int
    seller_name: str
    seller_type: str
    seller_link: str
    seller_logo_url: str
    seller_store_id: int
    seller_is_best_store: bool
    is_seller: bool
    is_seller_in_chat_whitelist: bool
    is_offline_installment_supported: bool
    store_rating: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
    
    