from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Category(Base):
    __tablename__ = "categories"
    category_id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=True)
    path: Mapped[str] = mapped_column(nullable=True)

class CategoryCreate(BaseModel):
    category_id: str
    name: str
    path : str