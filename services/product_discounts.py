from models.product_discounts import ProductDiscount, ProductDiscountCreate, ProductDiscountResponse
from repositories.product_discounts import ProductDiscountRepositories

class ProductDiscountService:
    @staticmethod
    def create(product_discount: ProductDiscountCreate) -> ProductDiscountResponse:
        """
        Create a new product discount.
        """
        return ProductDiscountRepositories.create(product_discount)

    @staticmethod
    def delete(product_id: int, discount_id: int):
        """
        Delete a product discount by ID.
        """
        return ProductDiscountRepositories.delete(product_id, discount_id)

    @staticmethod
    def get(product_id: int, discount_id: int):
        """
        Get a product discount by ID.
        """
        return ProductDiscountRepositories.get(product_id, discount_id)

    @staticmethod
    def update(product_id: int, discount_id: int, data):
        """
        Update a product discount by ID.
        """
        return ProductDiscountRepositories.update(product_id, discount_id, data)