from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"
    
    coupon_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    discount_type: Mapped[str] = mapped_column(String, nullable=False)  # percentage, fixed_amount
    discount_value: Mapped[float] = mapped_column(Numeric, nullable=False)
    min_order_value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    max_discount: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    usage_limit: Mapped[Optional[int]] = mapped_column(nullable=True)
    usage_count: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    coupon_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class CouponCreate(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    min_order_value: Optional[float] = None
    max_discount: Optional[float] = None
    start_date: datetime
    end_date: datetime
    usage_limit: Optional[int] = None
    coupon_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CouponUpdate(BaseModel):
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_value: Optional[float] = None
    max_discount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    usage_limit: Optional[int] = None
    is_active: Optional[bool] = None
    coupon_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CouponResponse(BaseModel):
    coupon_id: int
    code: str
    description: Optional[str]
    discount_type: str
    discount_value: float
    min_order_value: Optional[float]
    max_discount: Optional[float]
    start_date: datetime
    end_date: datetime
    usage_limit: Optional[int]
    usage_count: int
    is_active: bool
    coupon_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 