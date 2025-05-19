from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, TIMESTAMP, String, ARRAY, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductEmbedding(Base, TimestampMixin):
    __tablename__ = "product_embeddings"
    
    embedding_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), nullable=False)
    embedding_type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "text", "image"
    embedding_vector: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=False)
    embedding_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class ProductEmbeddingCreate(BaseModel):
    product_id: int
    embedding_type: str
    embedding_vector: List[float]
    embedding_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductEmbeddingUpdate(BaseModel):
    embedding_type: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    embedding_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductEmbeddingResponse(BaseModel):
    embedding_id: int
    product_id: int
    embedding_type: str
    embedding_vector: List[float]
    embedding_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 