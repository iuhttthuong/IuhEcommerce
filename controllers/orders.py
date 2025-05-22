from fastapi import APIRouter
from typing import List
from models.orders import Order, OrderCreate, OrderUpdate, OrderModel
from services.orders import OrderService    

router = APIRouter()

@router.post("/", response_model=OrderModel)
def create_order(order: OrderCreate) -> OrderModel:
    return OrderService.create_order(order)

@router.get("/{order_id}", response_model=OrderModel)
def get_order(order_id: int) -> OrderModel:
    return OrderService.get_order_by_id(order_id)

@router.put("/{order_id}", response_model=OrderModel)
def update_order(order_id: int, order: OrderUpdate) -> OrderModel:
    return OrderService.update_order(order_id, order)

@router.delete("/{order_id}", response_model=OrderModel)
def delete_order(order_id: int) -> bool:
    return OrderService.delete_order(order_id)

@router.get("/user/{user_id}", response_model=List[OrderModel])
def get_orders_by_user(user_id: int) -> List[OrderModel]:
    return OrderService.get_by_user_id(user_id)
