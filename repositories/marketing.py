from sqlalchemy.orm import Session
from models.coupons import Coupon, CouponCreate, CouponUpdate
from typing import List, Optional
from datetime import datetime

class MarketingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_shop(self, shop_id: int) -> List[Coupon]:
        """Get all coupons for a shop"""
        return self.db.query(Coupon).all()

    def get_by_id(self, coupon_id: int) -> Optional[Coupon]:
        """Get a marketing campaign by ID"""
        return self.db.query(Coupon).filter(Coupon.coupon_id == coupon_id).first()

    def create(self, coupon: CouponCreate) -> Coupon:
        """Create a new marketing campaign"""
        db_coupon = Coupon(**coupon.model_dump())
        self.db.add(db_coupon)
        self.db.commit()
        self.db.refresh(db_coupon)
        return db_coupon

    def update(self, coupon_id: int, coupon: CouponUpdate) -> Optional[Coupon]:
        """Update a marketing campaign"""
        db_coupon = self.get_by_id(coupon_id)
        if db_coupon:
            update_data = coupon.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_coupon, key, value)
            self.db.commit()
            self.db.refresh(db_coupon)
        return db_coupon

    def delete(self, coupon_id: int) -> bool:
        """Delete a marketing campaign"""
        db_coupon = self.get_by_id(coupon_id)
        if db_coupon:
            self.db.delete(db_coupon)
            self.db.commit()
            return True
        return False

    def get_active_campaigns(self) -> List[Coupon]:
        """Get all active marketing campaigns"""
        current_time = datetime.now()
        return self.db.query(Coupon).filter(
            Coupon.start_date <= current_time,
            Coupon.end_date >= current_time,
            Coupon.is_active == True
        ).all()

    def get_upcoming_campaigns(self) -> List[Coupon]:
        """Get all upcoming marketing campaigns"""
        current_time = datetime.now()
        return self.db.query(Coupon).filter(
            Coupon.start_date > current_time,
            Coupon.is_active == True
        ).all()

    def get_past_campaigns(self) -> List[Coupon]:
        """Get all past marketing campaigns"""
        current_time = datetime.now()
        return self.db.query(Coupon).filter(
            Coupon.end_date < current_time
        ).all() 