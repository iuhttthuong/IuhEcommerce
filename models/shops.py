from datetime import datetime
from sqlalchemy import DECIMAL
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Shop(Base, TimestampMixin):
    __tablename__ = "shops"
    shop_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    shop_name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    logo_url: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    rating: Mapped[float] = mapped_column(DECIMAL, nullable=True)

class ShopCreate(BaseModel):
    username: str
    shop_name: str
    description: str | None = None
    logo_url: str | None = None
    is_active: bool = True
    rating: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
