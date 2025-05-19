from typing import Optional
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
import sqlalchemy as sa
from models.base import Base

class Shop(Base):
    __tablename__ = "shops"

    seller_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mail: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ShopCreate(BaseModel):
    username: str
    password: str
    name: str
    mail: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ShopUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    mail: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ShopResponse(BaseModel):
    seller_id: int
    username: str
    name: str
    mail: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ShopModel(BaseModel):
    shop_id: int
    name: str
    description: Optional[str]
    logo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True 