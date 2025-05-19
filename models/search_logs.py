from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class SearchLog(Base, TimestampMixin):
    __tablename__ = "search_logs"
    
    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    query: Mapped[str] = mapped_column(String, nullable=False)
    filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result_count: Mapped[int] = mapped_column(default=0)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    search_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class SearchLogCreate(BaseModel):
    user_id: Optional[int] = None
    query: str
    filters: Optional[dict] = None
    result_count: int = 0
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    search_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class SearchLogUpdate(BaseModel):
    result_count: Optional[int] = None
    search_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class SearchLogResponse(BaseModel):
    log_id: int
    user_id: Optional[int]
    query: str
    filters: Optional[dict]
    result_count: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    search_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 