from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Text, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
import enum
from models.base import Base, TimestampMixin


class PromotionType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"
    BUY_X_GET_Y = "buy_x_get_y"


class Promotion(Base, TimestampMixin):
    __tablename__ = "promotions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[PromotionType] = mapped_column(Enum(PromotionType), nullable=False)
    value: Mapped[float] = mapped_column(nullable=False)  # Percentage or fixed amount
    min_order_value: Mapped[Optional[float]] = mapped_column()
    max_discount: Mapped[Optional[float]] = mapped_column()
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_limit: Mapped[Optional[int]] = mapped_column()  # Maximum number of times this promotion can be used
    usage_count: Mapped[int] = mapped_column(default=0)  # Number of times this promotion has been used
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.product_id"))  # Optional: specific product
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.category_id"))  # Optional: specific category
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    shop = relationship("Shop", back_populates="promotions")
    product = relationship("Product", back_populates="promotions")
    category = relationship("Category", back_populates="promotions")


class PromotionCreate(BaseModel):
    shop_id: int
    name: str
    code: str
    type: PromotionType
    value: float
    start_date: datetime
    end_date: datetime
    min_order_value: Optional[float] = None
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None


class PromotionUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[float] = None
    min_order_value: Optional[float] = None
    max_discount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    usage_limit: Optional[int] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None


class PromotionResponse(BaseModel):
    id: int
    shop_id: int
    name: str
    code: str
    type: PromotionType
    value: float
    min_order_value: Optional[float]
    max_discount: Optional[float]
    start_date: datetime
    end_date: datetime
    is_active: bool
    usage_limit: Optional[int]
    usage_count: int
    product_id: Optional[int]
    category_id: Optional[int]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 