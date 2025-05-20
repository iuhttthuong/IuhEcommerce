from datetime import datetime
from sqlalchemy import DECIMAL, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, EmailStr
from models.base import Base, TimestampMixin
from typing import List

class Shop(Base, TimestampMixin):
    __tablename__ = "shops"
    shop_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    shop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    rating: Mapped[float] = mapped_column(DECIMAL(3,2), nullable=True)
    last_login: Mapped[datetime] = mapped_column(nullable=True)

    # Add relationship to products
    products: Mapped[List["Product"]] = relationship("Product", back_populates="shop", foreign_keys="Product.seller_id", primaryjoin="Shop.shop_id == Product.seller_id")
    chat_sessions: Mapped[List["Chat"]] = relationship("Chat", back_populates="shop")
    promotions: Mapped[List["Promotion"]] = relationship("Promotion", back_populates="shop")
    finances: Mapped[List["Finance"]] = relationship("Finance", back_populates="shop")
    analytics: Mapped[List["Analytics"]] = relationship("Analytics", back_populates="shop")
    customer_service_tickets: Mapped[List["CustomerService"]] = relationship("CustomerService", back_populates="shop")
    policies: Mapped[List["Policy"]] = relationship("Policy", back_populates="shop")

class ShopCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    shop_name: str
    description: str | None = None
    logo_url: str | None = None
    address: str | None = None
    phone: str | None = None
    is_active: bool = True
    rating: float | None = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ShopModel(BaseModel):
    shop_id: int
    username: str
    email: str
    shop_name: str
    description: str | None = None
    logo_url: str | None = None
    address: str | None = None
    phone: str | None = None
    is_active: bool
    rating: float | None = None
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
