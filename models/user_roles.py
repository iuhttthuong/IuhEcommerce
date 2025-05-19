from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class UserRole(Base, TimestampMixin):
    __tablename__ = "user_roles"
    
    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    role_name: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "admin", "customer", "seller"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    permissions: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # JSON string of permissions

class UserRoleCreate(BaseModel):
    user_id: int
    role_name: str
    description: Optional[str] = None
    permissions: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UserRoleUpdate(BaseModel):
    role_name: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    permissions: Optional[str] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UserRoleResponse(BaseModel):
    role_id: int
    user_id: int
    role_name: str
    is_active: bool
    description: Optional[str]
    permissions: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 