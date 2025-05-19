from db import Session
from models.cart_items import CartItem
from models.shopping_carts import ShoppingCart, ShoppingCartCreate, ShoppingCartModel
from datetime import datetime

class ShoppingCartRepository:
    @staticmethod
    def create(payload: ShoppingCartCreate) -> ShoppingCartModel:
        with Session() as session:
            cart = ShoppingCart(**payload.model_dump(), created_at=datetime.now(), updated_at=datetime.now())
            session.add(cart)
            session.commit()
            session.refresh(cart)
            return ShoppingCartModel.model_validate(cart)
    @staticmethod
    def get(cart_id: int) -> ShoppingCartModel:
        with Session() as session:
            cart = session.get(ShoppingCart, cart_id)
            if not cart:
                raise ValueError(f"Shopping Cart with ID {cart_id} not found")
            return ShoppingCartModel.model_validate(cart)
    @staticmethod
    def update(cart_id: int, data: ShoppingCartCreate) -> ShoppingCartModel:
        with Session() as session:
            cart = session.get(ShoppingCart, cart_id)
            if not cart:
                raise ValueError(f"Shopping Cart with ID {cart_id} not found")

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(cart, field, value)

            session.commit()
            session.refresh(cart)
            return ShoppingCartModel.model_validate(cart)
    @staticmethod
    def delete(cart_id: int):
        with Session() as session:
            cart = session.get(ShoppingCart, cart_id)
            if not cart:
                raise ValueError(f"Shopping Cart with ID {cart_id} not found")

            # Xóa các cart_items trước
            session.query(CartItem).filter(CartItem.cart_id == cart_id).delete()

            # Sau đó xóa shopping cart
            session.delete(cart)
            session.commit()
            return True


    @staticmethod
    def get_shopping_cart_by_customer_id(customer_id: int) -> list[ShoppingCartModel]:
        with Session() as session:
            cart = session.query(ShoppingCart).filter(ShoppingCart.customer_id == customer_id).all()
            if not cart:
                raise ValueError(f"Shopping Cart with Customer ID {customer_id} not found")
            return [ShoppingCartModel.model_validate(item) for item in cart]