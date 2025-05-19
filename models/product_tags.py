from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductTag(Base, TimestampMixin):
    __tablename__ = "product_tags"
    
    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tag_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class ProductTagCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    tag_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductTagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    tag_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductTagResponse(BaseModel):
    tag_id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool
    tag_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 