from models.orders import Order, OrderUpdate, OrderCreate, OrderModel
from repositories.orders import OrderRepository

class OrderService:     
    @staticmethod
    def create_order(order: OrderCreate) -> OrderModel:
        order_repository = OrderRepository()
        return order_repository.create_order(order)
    @staticmethod
    def get_order_by_id(order_id: int) -> OrderModel:
        order_repository = OrderRepository()
        return order_repository.get_order_by_id(order_id)
    @staticmethod
    def update_order(order_id: int, order_update: OrderUpdate) -> OrderModel:
        order_repository = OrderRepository()
        return order_repository.update_order(order_id, order_update)
    @staticmethod
    def delete_order(order_id: int) -> bool:
        order_repository = OrderRepository()
        return order_repository.delete_order(order_id)
    @staticmethod
    def get_by_user_id(user_id: int) -> list[OrderModel]:
        order_repository = OrderRepository()
        return order_repository.get_by_user_id(user_id)
    