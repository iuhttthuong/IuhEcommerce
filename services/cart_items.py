from models.cart_items import CartItem, CartItemCreate, CartItemModel
from repositories.cart_items import CartItemRepository

class CartItemService:
    @staticmethod
    def create(cart_item: CartItemCreate) -> CartItemModel:
        cart_item = CartItemRepository.create(cart_item)
        return CartItemModel.from_orm(cart_item)
    @staticmethod
    def get(cart_id: int, product_id: int) -> CartItemModel:
        cart_item = CartItemRepository.get(cart_id, product_id)
        return CartItemModel.from_orm(cart_item)
    @staticmethod
    def update(cart_id: int, product_id: int, data: CartItemCreate) -> CartItemModel:
        cart_item = CartItemRepository.update(cart_id, product_id, data)
        return CartItemModel.from_orm(cart_item)
    @staticmethod
    def delete(cart_id: int, product_id: int) -> None:
        CartItemRepository.delete(cart_id, product_id)
    @staticmethod
    def get_cart_items_by_cart_id(cart_id: int) -> list[CartItemModel]:
        cart_items = CartItemRepository.get_cart_items_by_cart_id(cart_id)
        return [CartItemModel.from_orm(item) for item in cart_items]