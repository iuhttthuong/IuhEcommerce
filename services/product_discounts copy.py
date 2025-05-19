from models.product_discounts import ProductDiscount, ProductDiscountCreate
from repositories.product_discounts import ProductDiscountRepositories

class ProductDiscountService:
    @staticmethod
    def create(payload: ProductDiscountCreate):
        """
        Create a new product discount.
        """
        return ProductDiscountRepositories.create(payload)

    @staticmethod
    def delete(id: int):
        """
        Delete a product discount by ID.
        """
        return ProductDiscountRepositories.delete(id)