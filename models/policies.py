from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import ForeignKey, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class Policy(Base, TimestampMixin):
    __tablename__ = "policies"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # return, shipping, payment, privacy, terms
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_date: Mapped[datetime] = mapped_column(nullable=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    policy_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional data like requirements, conditions, etc.
    
    # Relationships
    shop = relationship("Shop", back_populates="policies")


class PolicyCreate(BaseModel):
    shop_id: int
    type: str
    title: str
    content: str
    version: str
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    policy_metadata: Optional[Dict[str, Any]] = None


class PolicyUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    policy_metadata: Optional[Dict[str, Any]] = None


class PolicyResponse(BaseModel):
    id: int
    shop_id: int
    type: str
    title: str
    content: str
    version: str
    is_active: bool
    effective_date: datetime
    expiry_date: Optional[datetime]
    policy_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 