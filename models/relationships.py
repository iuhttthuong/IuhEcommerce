from sqlalchemy.orm import relationship
from models.products import Product
from models.customers import Customer

def setup_relationships():
    # Setup Product relationships
    Product.reviews = relationship(
        "Review",
        back_populates="product",
        lazy="joined",
        cascade="all, delete-orphan"
    )

    # Setup Customer relationships
    Customer.reviews = relationship(
        "Review",
        back_populates="customer",
        lazy="joined",
        cascade="all, delete-orphan"
    ) 