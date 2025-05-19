from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from .models import ShopCreate, ShopUpdate, ShopResponse, ShopSettings

class ShopRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, shop: ShopCreate) -> ShopResponse:
        db_shop = ShopResponse(**shop.dict())
        self.db.add(db_shop)
        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop

    def get_by_id(self, shop_id: int) -> Optional[ShopResponse]:
        return self.db.query(ShopResponse).filter(ShopResponse.id == shop_id).first()

    def get_by_owner_id(self, owner_id: int) -> List[ShopResponse]:
        return self.db.query(ShopResponse).filter(ShopResponse.owner_id == owner_id).all()

    def update(self, shop_id: int, shop_update: ShopUpdate) -> ShopResponse:
        db_shop = self.get_by_id(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        
        update_data = shop_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shop, field, value)
        
        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop

    def delete(self, shop_id: int):
        db_shop = self.get_by_id(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        
        self.db.delete(db_shop)
        self.db.commit()

    def get_settings(self, shop_id: int) -> ShopSettings:
        db_shop = self.get_by_id(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        
        # Get settings from database
        # This is a simplified version - you would need to implement the actual database operations
        return ShopSettings()

    def update_settings(self, shop_id: int, settings: ShopSettings) -> ShopSettings:
        db_shop = self.get_by_id(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")
        
        # Update settings in database
        # This is a simplified version - you would need to implement the actual database operations
        return settings

    def get_shop_stats(self, shop_id: int) -> Dict[str, Any]:
        db_shop = self.get_by_id(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        # Get basic stats
        total_products = self.db.query(func.count(Product.id)).filter(
            Product.shop_id == shop_id
        ).scalar() or 0

        total_orders = self.db.query(func.count(Order.id)).filter(
            Order.shop_id == shop_id
        ).scalar() or 0

        total_revenue = self.db.query(func.sum(Order.total_amount)).filter(
            Order.shop_id == shop_id,
            Order.status == "completed"
        ).scalar() or 0.0

        average_rating = self.db.query(func.avg(Review.rating)).filter(
            Review.shop_id == shop_id
        ).scalar() or 0.0

        return {
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_rating": average_rating
        }

    def search_shops(self, query: str, limit: int = 10) -> List[ShopResponse]:
        return self.db.query(ShopResponse).filter(
            ShopResponse.name.ilike(f"%{query}%")
        ).limit(limit).all()

    def get_top_shops(self, limit: int = 10) -> List[ShopResponse]:
        return self.db.query(ShopResponse).order_by(
            ShopResponse.rating.desc()
        ).limit(limit).all()

    def get_recent_shops(self, limit: int = 10) -> List[ShopResponse]:
        return self.db.query(ShopResponse).order_by(
            ShopResponse.created_at.desc()
        ).limit(limit).all() 