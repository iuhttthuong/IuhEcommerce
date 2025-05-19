from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .models import ShopCreate, ShopUpdate, ShopResponse, ShopStats, ShopSettings
from db import Session
from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException

class ShopService:
    def __init__(self, db: DBSession):
        self.db = db

    def create_shop(self, shop: ShopCreate) -> ShopResponse:
        db_shop = ShopResponse(**shop.dict())
        self.db.add(db_shop)
        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop

    def get_shop(self, shop_id: int) -> ShopResponse:
        shop = self.db.query(ShopResponse).filter(ShopResponse.id == shop_id).first()
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        return shop

    def update_shop(self, shop_id: int, shop_update: ShopUpdate) -> ShopResponse:
        db_shop = self.get_shop(shop_id)
        update_data = shop_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shop, field, value)
        db_shop.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop

    def delete_shop(self, shop_id: int):
        db_shop = self.get_shop(shop_id)
        self.db.delete(db_shop)
        self.db.commit()

    def get_shop_stats(self, shop_id: int, start_date: Optional[datetime] = None) -> ShopStats:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)

        # Get basic stats
        total_products = self.db.query(Product).filter(Product.shop_id == shop_id).count()
        total_orders = self.db.query(Order).filter(Order.shop_id == shop_id).count()
        total_revenue = self.db.query(Order).filter(
            Order.shop_id == shop_id,
            Order.status == "completed"
        ).with_entities(func.sum(Order.total_amount)).scalar() or 0.0

        # Get average rating
        average_rating = self.db.query(Review).filter(
            Review.shop_id == shop_id
        ).with_entities(func.avg(Review.rating)).scalar() or 0.0

        # Get monthly sales
        monthly_sales = {}
        sales_data = self.db.query(
            func.date_trunc('month', Order.created_at).label('month'),
            func.sum(Order.total_amount).label('total')
        ).filter(
            Order.shop_id == shop_id,
            Order.status == "completed",
            Order.created_at >= start_date
        ).group_by('month').all()

        for month, total in sales_data:
            monthly_sales[month.strftime('%Y-%m')] = float(total)

        # Get top products
        top_products = self.db.query(
            Product,
            func.count(OrderItem.id).label('order_count'),
            func.sum(OrderItem.quantity).label('total_quantity')
        ).join(OrderItem).filter(
            Product.shop_id == shop_id
        ).group_by(Product.id).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()

        top_products_list = [
            {
                "id": p.id,
                "name": p.name,
                "order_count": count,
                "total_quantity": quantity
            }
            for p, count, quantity in top_products
        ]

        # Get recent orders
        recent_orders = self.db.query(Order).filter(
            Order.shop_id == shop_id
        ).order_by(Order.created_at.desc()).limit(5).all()

        recent_orders_list = [
            {
                "id": o.id,
                "customer_id": o.customer_id,
                "total_amount": o.total_amount,
                "status": o.status,
                "created_at": o.created_at
            }
            for o in recent_orders
        ]

        return ShopStats(
            total_products=total_products,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_rating=average_rating,
            monthly_sales=monthly_sales,
            top_products=top_products_list,
            recent_orders=recent_orders_list
        )

    def update_shop_settings(self, shop_id: int, settings: ShopSettings) -> ShopSettings:
        db_shop = self.get_shop(shop_id)
        # Update settings in database
        # This is a simplified version - you would need to implement the actual database operations
        return settings

    def get_shop_settings(self, shop_id: int) -> ShopSettings:
        db_shop = self.get_shop(shop_id)
        # Get settings from database
        # This is a simplified version - you would need to implement the actual database operations
        return ShopSettings() 