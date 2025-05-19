from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class Session(Base, TimestampMixin):
    __tablename__ = "sessions"
    
    session_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    device_info: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    session_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class SessionCreate(BaseModel):
    user_id: int
    token: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    expires_at: datetime
    session_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class SessionUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    session_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class SessionResponse(BaseModel):
    session_id: int
    user_id: int
    token: str
    device_info: Optional[str]
    ip_address: Optional[str]
    is_active: bool
    expires_at: datetime
    last_activity: datetime
    session_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 