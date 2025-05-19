from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class CustomerCoupon(Base, TimestampMixin):
    __tablename__ = "customer_coupons"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.coupon_id"), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.order_id"), nullable=True)
    customer_coupon_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class CustomerCouponCreate(BaseModel):
    user_id: int
    coupon_id: int
    customer_coupon_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CustomerCouponUpdate(BaseModel):
    is_used: Optional[bool] = None
    used_at: Optional[datetime] = None
    order_id: Optional[int] = None
    customer_coupon_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CustomerCouponResponse(BaseModel):
    id: int
    user_id: int
    coupon_id: int
    is_used: bool
    used_at: Optional[datetime]
    order_id: Optional[int]
    customer_coupon_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 