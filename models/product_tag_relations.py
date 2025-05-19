from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductTagRelation(Base, TimestampMixin):
    __tablename__ = "product_tag_relations"
    
    relation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("product_tags.tag_id"), nullable=False)
    relation_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class ProductTagRelationCreate(BaseModel):
    product_id: int
    tag_id: int
    relation_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductTagRelationUpdate(BaseModel):
    relation_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductTagRelationResponse(BaseModel):
    relation_id: int
    product_id: int
    tag_id: int
    relation_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 