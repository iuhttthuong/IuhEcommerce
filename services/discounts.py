from models.discounts import Discount, DiscountCreate
from repositories.discounts import DiscountRepositories

class DiscountService:
    @staticmethod
    def create(payload: DiscountCreate):
        return DiscountRepositories.create(payload)

    @staticmethod
    def delete(discount_id: int):
        return DiscountRepositories.delete(discount_id)