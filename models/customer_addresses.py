from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, TIMESTAMP, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base, TimestampMixin

class CustomerAddress(Base, TimestampMixin):
    __tablename__ = "customer_addresses"
    
    address_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    address_line1: Mapped[str] = mapped_column(String, nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    address_type: Mapped[str] = mapped_column(String, nullable=False)  # home, work, other
    address_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class CustomerAddressCreate(BaseModel):
    user_id: int
    full_name: str
    phone_number: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False
    address_type: str = "home"
    address_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CustomerAddressUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None
    address_type: Optional[str] = None
    address_metadata: Optional[dict] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CustomerAddressResponse(BaseModel):
    address_id: int
    user_id: int
    full_name: str
    phone_number: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    address_type: str
    address_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True 