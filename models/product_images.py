from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base

    
class ProductImage(Base):
    __tablename__ = "product_images"
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id"))
    base_url: Mapped[str] = mapped_column(nullable=False)
    large_url: Mapped[str] = mapped_column(nullable=False)
    medium_url: Mapped[str] = mapped_column(nullable=False)


class ProductImageCreate(BaseModel):
    product_id: str
    base_url: str
    large_url: str
    medium_url: str

    