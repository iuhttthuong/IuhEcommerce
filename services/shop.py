from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.shop import Shop
from models.shop import ShopCreate, ShopUpdate, ShopResponse

class ShopService:
    def __init__(self, db: Session):
        self.db = db

    def get_shop(self, shop_id: int) -> Optional[Shop]:
        """Get a shop by ID."""
        return self.db.query(Shop).filter(Shop.shop_id == shop_id).first()

    def get_shops(self, skip: int = 0, limit: int = 100) -> List[Shop]:
        """Get a list of shops with pagination."""
        return self.db.query(Shop).offset(skip).limit(limit).all()

    def create_shop(self, shop: ShopCreate) -> Shop:
        """Create a new shop."""
        db_shop = Shop(**shop.model_dump())
        self.db.add(db_shop)
        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop

    def update_shop(self, shop_id: int, shop: ShopUpdate) -> Shop:
        """Update a shop."""
        db_shop = self.get_shop(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        update_data = shop.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shop, field, value)

        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop

    def delete_shop(self, shop_id: int) -> bool:
        """Delete a shop."""
        db_shop = self.get_shop(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        self.db.delete(db_shop)
        self.db.commit()
        return True

    def get_shop_by_owner(self, owner_id: int) -> List[Shop]:
        """Get all shops owned by a user."""
        return self.db.query(Shop).filter(Shop.owner_id == owner_id).all()

    def get_active_shops(self) -> List[Shop]:
        """Get all active shops."""
        return self.db.query(Shop).filter(Shop.status == "active").all()

    def update_shop_stats(self, shop_id: int, stats: dict) -> Shop:
        """Update shop statistics."""
        db_shop = self.get_shop(shop_id)
        if not db_shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        for field, value in stats.items():
            if hasattr(db_shop, field):
                setattr(db_shop, field, value)

        self.db.commit()
        self.db.refresh(db_shop)
        return db_shop 