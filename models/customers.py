#lib
from datetime import datetime
from models.base import Base, TimestampMixin
from sqlalchemy import  String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from pydantic import BaseModel, ConfigDict

class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column( primary_key=True)
    customer_fname: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_lname: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_mail: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    customer_address: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_dob: Mapped[datetime] = mapped_column(String(20), nullable=False)
    customer_gender: Mapped[str] = mapped_column(String(10), nullable=False)

    # Relationships
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="customer")
    service_tickets: Mapped[List["CustomerService"]] = relationship("CustomerService", back_populates="customer", foreign_keys="CustomerService.customer_id")
    assigned_tickets: Mapped[List["CustomerService"]] = relationship("CustomerService", back_populates="assignee", foreign_keys="CustomerService.assigned_to")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="customer")

class CustomerCreate(BaseModel):
    customer_fname: str
    customer_lname: str
    customer_mail: str
    customer_address: str
    customer_phone: str
    customer_dob: datetime
    customer_gender: str
    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class CustomerModel(BaseModel):
    customer_id: int
    customer_fname: str
    customer_lname: str
    customer_mail: str
    customer_address: str
    customer_phone: str
    customer_dob: datetime
    customer_gender: str
    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True

class UpdateCustomerPayload(BaseModel):
    customer_fname: str = None
    customer_lname: str = None
    customer_mail: str = None
    customer_address: str = None
    customer_phone: str = None
    customer_dob: datetime = None
    customer_gender: str = None
    class Config:
        from_attributes = True
        arbitrary_types_allowed=True
        from_attributes = True
        validate_by_name = True
        use_enum_values = True