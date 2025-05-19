from db import Session
from models.product_discounts import ProductDiscount, ProductDiscountCreate, ProductDiscountResponse
from models.products import Product
from models.discounts import Discount

class ProductDiscountRepositories:
    @staticmethod
    def create(product_discount: ProductDiscountCreate) -> ProductDiscount:
        with Session() as session:
            # Check if discount_id exists
            discount = session.query(Discount).filter(Discount.discount_id == product_discount.discount_id).first()
            if not discount:
                raise ValueError(f"Discount with ID {product_discount.discount_id} does not exist")
            product_discount = ProductDiscount(**product_discount.model_dump())
            session.add(product_discount)
            session.commit()
            session.refresh(product_discount)
            return product_discount

    @staticmethod
    def get(product_id: int, discount_id: int) -> ProductDiscountResponse:
        with Session() as session:
            product_discount = session.get(ProductDiscount, (product_id, discount_id))
            if not product_discount:
                raise ValueError(f"Product discount with product_id={product_id} and discount_id={discount_id} not found")
            return ProductDiscountResponse.model_validate(product_discount)

    @staticmethod
    def update(product_id: int, discount_id: int, data: ProductDiscountCreate) -> ProductDiscountResponse:
        with Session() as session:
            product_discount = session.get(ProductDiscount, (product_id, discount_id))
            if not product_discount:
                raise ValueError(f"Product discount with product_id={product_id} and discount_id={discount_id} not found")

            for field, value in data.model_dump(exclude_unset=True).items():
                if field not in ['product_id', 'discount_id']:
                    setattr(product_discount, field, value)

            session.commit()
            session.refresh(product_discount)
            return ProductDiscountResponse.model_validate(product_discount)

    @staticmethod
    def delete(product_id: int, discount_id: int):
        with Session() as session:
            product_discount = session.get(ProductDiscount, (product_id, discount_id))
            if not product_discount:
                raise ValueError(f"Product discount with product_id={product_id} and discount_id={discount_id} not found")
            session.delete(product_discount)
            session.commit()
            # Return the deleted object as response
            return ProductDiscountResponse.model_validate(product_discount)

    @staticmethod
    def get_by_product_id(product_id: int) -> list[ProductDiscountResponse]:
        with Session() as session:
            product_discounts = session.query(ProductDiscount).filter(ProductDiscount.product_id == product_id).all()
            return [ProductDiscountResponse.model_validate(pd) for pd in product_discounts]

    @staticmethod
    def get_by_discount_id(discount_id: int) -> list[ProductDiscountResponse]:
        with Session() as session:
            product_discounts = session.query(ProductDiscount).filter(ProductDiscount.discount_id == discount_id).all()
            return [ProductDiscountResponse.model_validate(pd) for pd in product_discounts]