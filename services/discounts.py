from models.discounts import Discount, DiscountCreate, DiscountModel
from repositories.discounts import DiscountRepositories
from sqlalchemy.orm import Session
from db import SessionLocal

class DiscountService:
    @staticmethod
    def create_discount(payload: DiscountCreate):
        return DiscountRepositories.create(payload)

    @staticmethod
    def delete(discount_id: int):
        return DiscountRepositories.delete(discount_id)

    @staticmethod
    def list_discounts():
        with SessionLocal() as session:
            return session.query(Discount).all()

    @staticmethod
    def get_discount(discount_id: int):
        with SessionLocal() as session:
            return session.query(Discount).filter(Discount.discount_id == discount_id).first()

    @staticmethod
    def update_discount(discount_id: int, payload: DiscountCreate):
        return DiscountRepositories.update(discount_id, payload)
    
    @staticmethod
    def delete_discount(discount_id: int):
        return DiscountRepositories.delete(discount_id)

    
