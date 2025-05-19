from models.product_discounts import ProductDiscount, ProductDiscountCreate, ProductDiscountModel
from db import Session

class ProductDiscountRepositories:
    @staticmethod
    def create(payload: ProductDiscountCreate):
        with Session() as session:
            new_product_discount = ProductDiscount(**payload.model_dump())
            session.add(new_product_discount)
            session.commit()
            session.refresh(new_product_discount)
            
            return ProductDiscountModel.model_validate(new_product_discount)

    @staticmethod
    def delete(id: int):
        with Session() as session:
            product_discount = session.get(ProductDiscount, id)
            if not product_discount:
                return None
            session.delete(product_discount)
            session.commit()
            return ProductDiscountModel.model_validate(product_discount)