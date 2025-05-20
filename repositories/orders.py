from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.orders import Order, OrderCreate, OrderUpdate, OrderResponse
from models.order_items import OrderItem
from models.order_status import OrderStatus
from models.payments import Payment
from models.shipping import Shipping
from models.customers import Customer


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order_data: OrderCreate) -> Order:
        """Create a new order"""
        order = Order(**order_data.dict())
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get an order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_by_shop(self, shop_id: int) -> List[Order]:
        """Get all orders for a shop"""
        return self.db.query(Order).filter(Order.shop_id == shop_id).all()

    def get_by_customer(self, customer_id: int) -> List[Order]:
        """Get all orders for a customer"""
        return self.db.query(Order).filter(Order.customer_id == customer_id).all()

    def update(self, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
        """Update an order"""
        order = self.get_by_id(order_id)
        if order:
            for key, value in order_data.dict(exclude_unset=True).items():
                setattr(order, key, value)
            self.db.commit()
            self.db.refresh(order)
        return order

    def delete(self, order_id: int) -> bool:
        """Delete an order"""
        order = self.get_by_id(order_id)
        if order:
            self.db.delete(order)
            self.db.commit()
            return True
        return False

    def get_order_details(self, order_id: int) -> Dict[str, Any]:
        """Get detailed order information including items, status, payment, and shipping"""
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Get order items
        items = self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        
        # Get order status history
        status_history = self.db.query(OrderStatus).filter(OrderStatus.order_id == order_id).all()
        
        # Get payment information
        payment = self.db.query(Payment).filter(Payment.order_id == order_id).first()
        
        # Get shipping information
        shipping = self.db.query(Shipping).filter(Shipping.order_id == order_id).first()
        
        # Get customer information
        customer = self.db.query(Customer).filter(Customer.id == order.customer_id).first()

        return {
            "order": OrderResponse.model_validate(order),
            "items": items,
            "status_history": status_history,
            "payment": payment,
            "shipping": shipping,
            "customer": customer
        }

    def get_shop_order_stats(self, shop_id: int) -> Dict[str, Any]:
        """Get order statistics for a shop"""
        total_orders = self.db.query(Order).filter(Order.shop_id == shop_id).count()
        pending_orders = self.db.query(Order).filter(
            Order.shop_id == shop_id,
            Order.status == "pending"
        ).count()
        completed_orders = self.db.query(Order).filter(
            Order.shop_id == shop_id,
            Order.status == "completed"
        ).count()
        cancelled_orders = self.db.query(Order).filter(
            Order.shop_id == shop_id,
            Order.status == "cancelled"
        ).count()

        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders
        }

    def update_order_status(self, order_id: int, new_status: str, note: Optional[str] = None) -> Optional[Order]:
        """Update order status and add status history"""
        order = self.get_by_id(order_id)
        if order:
            # Update order status
            order.status = new_status
            self.db.commit()

            # Add status history
            status_history = OrderStatus(
                order_id=order_id,
                status=new_status,
                note=note
            )
            self.db.add(status_history)
            self.db.commit()
            self.db.refresh(order)
        return order

    def get_recent_orders(self, shop_id: int, limit: int = 10) -> List[Order]:
        """Get recent orders for a shop"""
        return (
            self.db.query(Order)
            .filter(Order.shop_id == shop_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        ) 