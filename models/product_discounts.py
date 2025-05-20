from datetime import datetime
from sqlalchemy import ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base
from models.products import Product
from models.discounts import Discount

class ProductDiscount(Base):
    __tablename__ = "product_discounts"
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.product_id), primary_key=True)
    discount_id: Mapped[int] = mapped_column(ForeignKey(Discount.discount_id), primary_key=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", backref="product_discounts", overlaps="discounts,products")
    discount: Mapped["Discount"] = relationship("Discount", backref="product_discounts", overlaps="discounts,products")

class ProductDiscountCreate(BaseModel):
    product_id: int
    discount_id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ProductDiscountResponse(BaseModel):
    product_id: int
    discount_id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True

class ProductDiscountModel(BaseModel):
    product_id: int
    discount_id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_by_name = True
        use_enum_values = True   