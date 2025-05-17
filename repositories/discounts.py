from models.discounts import Discount, DiscountCreate, DiscountModel
from db import Session

class DiscountRepositories:
    @staticmethod
    def create(payload: DiscountCreate):
        with Session() as session:
            new_discount = Discount(**payload.model_dump())
            session.add(new_discount)
            session.commit()
            session.refresh(new_discount)      
            return DiscountModel.model_validate(new_discount)

    @staticmethod
    def delete(discount_id: int):
        with Session() as session:
            discount = session.get(Discount, discount_id)
            if not discount:
                return None
            session.delete(discount)
            session.commit()
            return DiscountModel.model_validate(discount)