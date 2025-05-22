from db import Session
from models.orders import Order, OrderCreate, OrderUpdate, OrderModel

class OrderRepository:
    @staticmethod
    def create_order(payload: OrderCreate) -> OrderModel:
        with Session() as session:
            order = Order(**payload.dict())
            session.add(order)
            session.commit()
            session.refresh(order)
            return OrderModel.model_validate(order)

    @staticmethod
    def get_all() -> list[OrderModel]:
        with Session() as session:
            orders = session.query(Order).all()
            return [OrderModel.model_validate(order) for order in orders]

    @staticmethod
    def get_order_by_id(order_id: int) -> OrderModel | None:
        with Session() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            return OrderModel.model_validate(order) if order else None
    @staticmethod
    def update_order(order_id: int, payload: OrderUpdate) -> OrderModel | None:
        with Session() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                return None
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(order, key, value)
            session.commit()
            session.refresh(order)
            return OrderModel.model_validate(order)
    @staticmethod
    def delete_order(order_id: int) -> bool:
        with Session() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False
            session.delete(order)
            session.commit()
            return True
    @staticmethod
    def get_by_user_id(user_id: int) -> list[OrderModel]:
        with Session() as session:
            orders = session.query(Order).filter(Order.user_id == user_id).all()
            return [OrderModel.model_validate(order) for order in orders]