from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class UserRoleAssignment(Base, TimestampMixin):
    __tablename__ = "user_role_assignments"
    
    assignment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.role_id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    assignment_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class UserRoleAssignmentCreate(BaseModel):
    user_id: int
    role_id: int
    assigned_by: Optional[int] = None
    assignment_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UserRoleAssignmentUpdate(BaseModel):
    is_active: Optional[bool] = None
    assignment_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UserRoleAssignmentResponse(BaseModel):
    assignment_id: int
    user_id: int
    role_id: int
    is_active: bool
    assigned_by: Optional[int]
    assignment_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 