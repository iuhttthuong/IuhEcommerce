from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, EmailStr
from models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    user_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    user_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    user_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UserResponse(BaseModel):
    user_id: int
    email: str
    username: str
    full_name: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    last_login: Optional[datetime]
    user_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 