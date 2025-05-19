from db import Session
from models.cart_items import CartItem, CartItemCreate, CartItemModel
from datetime import datetime

class CartItemRepository:
    @staticmethod
    def create(payload: CartItemCreate) -> CartItemModel:
        with Session() as session:
            cart_item = CartItem(**payload.model_dump(), added_at=datetime.now())
            session.add(cart_item)
            session.commit()
            session.refresh(cart_item)
            return CartItemModel.model_validate(cart_item)

    @staticmethod
    def get(cart_id: int, product_id: int) -> CartItemModel:
        with Session() as session:
            cart_item = session.get(CartItem, (cart_id, product_id))
            if not cart_item:
                raise ValueError(f"Cart Item with Cart ID {cart_id} and Product ID {product_id} not found")
            return CartItemModel.model_validate(cart_item)

    @staticmethod
    def update(cart_id: int, product_id: int, quantity: int) -> CartItemModel:
        with Session() as session:
            cart_item = session.get(CartItem, (cart_id, product_id))
            if not cart_item:
                raise ValueError(f"Cart Item with Cart ID {cart_id} and Product ID {product_id} not found")

            cart_item.quantity = quantity

            session.commit()
            session.refresh(cart_item)
            return CartItemModel.model_validate(cart_item)

    @staticmethod
    def delete(cart_id: int, product_id: int):
        with Session() as session:
            cart_item = session.get(CartItem, (cart_id, product_id))
            if not cart_item:
                raise ValueError(f"Cart Item with Cart ID {cart_id} and Product ID {product_id} not found")

            session.delete(cart_item)
            session.commit()

    @staticmethod
    def get_cart_items_by_cart_id(cart_id: int) -> list[CartItemModel]:
        with Session() as session:
            cart_items = session.query(CartItem).filter(CartItem.cart_id == cart_id).all()
            return [CartItemModel.model_validate(item) for item in cart_items]