from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Brand(Base):
    __tablename__ = "brands"
    brand_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    brand_name: Mapped[str] = mapped_column(nullable=False)
    brand_slug: Mapped[str] = mapped_column(nullable=True)
    brand_country: Mapped[str] = mapped_column(nullable=True)

class BrandCreate(BaseModel):
    brand_id: int
    brand_name: str
    brand_slug: str
    brand_country: str
    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
    