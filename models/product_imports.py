from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class ProductImport(Base, TimestampMixin):
    __tablename__ = "product_imports"
    
    import_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # pending, processing, completed, failed
    total_products: Mapped[int] = mapped_column(default=0)
    imported_products: Mapped[int] = mapped_column(default=0)
    failed_products: Mapped[int] = mapped_column(default=0)
    import_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class ProductImportCreate(BaseModel):
    user_id: int
    total_products: int = 0
    import_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductImportUpdate(BaseModel):
    status: Optional[str] = None
    imported_products: Optional[int] = None
    failed_products: Optional[int] = None
    import_metadata: Optional[dict] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class ProductImportResponse(BaseModel):
    import_id: int
    user_id: int
    status: str
    total_products: int
    imported_products: int
    failed_products: int
    import_metadata: Optional[dict]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 