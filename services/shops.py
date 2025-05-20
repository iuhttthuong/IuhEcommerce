from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.shops import Shop, ShopCreate, ShopModel
from db import Session as DBSession
from passlib.context import CryptContext
import bcrypt

# Create password context with bcrypt to match pgcrypto's format
pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,  # Match pgcrypto's work factor
    bcrypt__ident="2a",  # Force $2a$ format to match pgcrypto
    deprecated="auto"
)

class ShopServices:
    @staticmethod
    def _hash_password(password: str, shop_id: int = None) -> str:
        """Hash a password using bcrypt to match pgcrypto format."""
        # Format password as 'shop{id}' to match SQL implementation
        if shop_id is not None:
            password = f'shop{shop_id}'
        
        # Use bcrypt directly to ensure $2a$ format
        salt = bcrypt.gensalt(rounds=12, prefix=b'2a')
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def get(shop_id: int) -> Optional[Shop]:
        """Get a shop by ID."""
        db = DBSession()
        try:
            return db.query(Shop).filter(Shop.shop_id == shop_id).first()
        finally:
            db.close()

    @staticmethod
    def get_all(skip: int = 0, limit: int = 100) -> List[Shop]:
        """Get a list of shops with pagination."""
        db = DBSession()
        try:
            return db.query(Shop).offset(skip).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def create(shop: ShopCreate) -> Shop:
        """Create a new shop."""
        db = DBSession()
        try:
            # Create a copy of the shop data
            shop_data = shop.model_dump()
            
            # Create the shop first to get the ID
            db_shop = Shop(**shop_data)
            db.add(db_shop)
            db.flush()  # This will generate the ID without committing
            
            # Now hash the password with the shop ID
            db_shop.password = ShopServices._hash_password(shop_data["password"], db_shop.shop_id)
            
            db.commit()
            db.refresh(db_shop)
            return db_shop
        finally:
            db.close()

    @staticmethod
    def update(shop_id: int, shop: ShopCreate) -> Shop:
        """Update a shop."""
        db = DBSession()
        try:
            db_shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
            if not db_shop:
                raise HTTPException(status_code=404, detail="Shop not found")

            update_data = shop.model_dump(exclude_unset=True)
            
            # Hash the password if it's being updated
            if "password" in update_data:
                update_data["password"] = ShopServices._hash_password(update_data["password"], shop_id)

            for field, value in update_data.items():
                setattr(db_shop, field, value)

            db.commit()
            db.refresh(db_shop)
            return db_shop
        finally:
            db.close()

    @staticmethod
    def delete(shop_id: int) -> bool:
        """Delete a shop."""
        db = DBSession()
        try:
            db_shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
            if not db_shop:
                raise HTTPException(status_code=404, detail="Shop not found")

            db.delete(db_shop)
            db.commit()
            return True
        finally:
            db.close()

    @staticmethod
    def get_shop_products(shop_id: int, offset: int = 0, limit: int = 10) -> List:
        """Get all products from a specific shop with pagination."""
        db = DBSession()
        try:
            shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
            if not shop:
                raise HTTPException(status_code=404, detail="Shop not found")
            return shop.products[offset:offset + limit]
        finally:
            db.close()

    @staticmethod
    def get_shop_stats(shop_id: int) -> dict:
        """Get shop statistics including total products, total sales, etc."""
        db = DBSession()
        try:
            shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
            if not shop:
                raise HTTPException(status_code=404, detail="Shop not found")
            
            return {
                "total_products": len(shop.products),
                "total_orders": len(shop.orders) if hasattr(shop, 'orders') else 0,
                "rating": shop.rating,
                "is_active": shop.is_active
            }
        finally:
            db.close()

    @staticmethod
    def search_shops(query: str, offset: int = 0, limit: int = 10) -> List[Shop]:
        """Search shops by name or description."""
        db = DBSession()
        try:
            return db.query(Shop).filter(
                (Shop.shop_name.ilike(f"%{query}%")) |
                (Shop.description.ilike(f"%{query}%"))
            ).offset(offset).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def get_top_shops(limit: int = 10) -> List[Shop]:
        """Get top performing shops based on sales and ratings."""
        db = DBSession()
        try:
            return db.query(Shop).filter(
                Shop.is_active == True
            ).order_by(Shop.rating.desc()).limit(limit).all()
        finally:
            db.close()

    @staticmethod
    def get_shop_by_owner(owner_id: int) -> List[Shop]:
        """Get all shops owned by a user."""
        db = DBSession()
        try:
            return db.query(Shop).filter(Shop.owner_id == owner_id).all()
        finally:
            db.close()

    @staticmethod
    def get_active_shops() -> List[Shop]:
        """Get all active shops."""
        db = DBSession()
        try:
            return db.query(Shop).filter(Shop.is_active == True).all()
        finally:
            db.close()

    @staticmethod
    def update_shop_stats(shop_id: int, stats: dict) -> Shop:
        """Update shop statistics."""
        db = DBSession()
        try:
            db_shop = db.query(Shop).filter(Shop.shop_id == shop_id).first()
            if not db_shop:
                raise HTTPException(status_code=404, detail="Shop not found")

            for field, value in stats.items():
                if hasattr(db_shop, field):
                    setattr(db_shop, field, value)

            db.commit()
            db.refresh(db_shop)
            return db_shop
        finally:
            db.close() 