from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

class Discount(Base):
    __tablename__ = "discounts"
    discount_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discount_name: Mapped[str] = mapped_column(nullable=False)
    discount_rate: Mapped[float] = mapped_column(nullable=False)
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    min_purchase_amount: Mapped[int] = mapped_column(nullable=False)
    max_discount_amount: Mapped[int] = mapped_column(nullable=False)

class DiscountCreate(BaseModel):
    discount_name: str
    discount_rate: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    min_purchase_amount: int
    max_discount_amount: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class DiscountResponse(BaseModel):
    discount_id: int
    discount_name: str
    discount_rate: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    min_purchase_amount: int
    max_discount_amount: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class DiscountUpdate(BaseModel):
    discount_name: str | None = None
    discount_rate: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_active: bool | None = None
    min_purchase_amount: int | None = None
    max_discount_amount: int | None = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class DiscountModel(BaseModel):
    discount_id: int
    discount_name: str
    discount_rate: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    min_purchase_amount: int
    max_discount_amount: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True