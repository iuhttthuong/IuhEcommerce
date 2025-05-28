from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

class Inventory(Base):
    __tablename__ = "inventories"
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    product_virtual_type: Mapped[str] = mapped_column(String, nullable=False)
    fulfillment_type: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    current_stock: Mapped[int] = mapped_column(nullable=True)

class InventoryCreate(BaseModel):
    product_id: str
    product_virtual_type: str
    fulfillment_type: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True
