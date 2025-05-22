from models.shopping_carts import ShoppingCart, ShoppingCartCreate, ShoppingCartModel
from repositories.shopping_carts import ShoppingCartRepository

class ShoppingCartService:
    @staticmethod
    def create(payload: ShoppingCartCreate) -> ShoppingCartModel:
        return ShoppingCartRepository.create(payload)
    @staticmethod
    def get(cart_id: int) -> ShoppingCartModel:
        return ShoppingCartRepository.get(cart_id)
    @staticmethod
    def update(cart_id: int, data: ShoppingCartCreate) -> ShoppingCartModel:
        return ShoppingCartRepository.update(cart_id, data)
    @staticmethod
    def delete(cart_id: int):
        return ShoppingCartRepository.delete(cart_id)
    @staticmethod
    def get_shopping_cart_by_customer_id(customer_id: int) -> ShoppingCartModel:
        return ShoppingCartRepository.get_shopping_cart_by_customer_id(customer_id)