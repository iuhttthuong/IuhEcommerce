from sqlalchemy.orm import Session
from models.inventories import Inventory, InventoryCreate
from typing import List, Optional, Dict, Any
from datetime import datetime

class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, inventory: InventoryCreate) -> Inventory:
        """Create a new inventory item"""
        db_inventory = Inventory(
            product_id=inventory.product_id,
            product_virtual_type=inventory.product_virtual_type,
            fulfillment_type=inventory.fulfillment_type,
            current_stock=0  # Default to 0 for new inventory
        )
        self.db.add(db_inventory)
        self.db.commit()
        self.db.refresh(db_inventory)
        return db_inventory

    async def get_by_product_id(self, product_id: str) -> Optional[Inventory]:
        """Get inventory item by product ID"""
        return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    async def get_by_virtual_type(self, virtual_type: int) -> List[Inventory]:
        """Get all inventory items for a virtual type"""
        return self.db.query(Inventory).filter(Inventory.product_virtual_type == virtual_type).all()

    async def update_stock(self, product_id: str, quantity_change: int) -> Optional[Inventory]:
        """Update inventory quantity"""
        db_inventory = await self.get_by_product_id(product_id)
        if db_inventory:
            db_inventory.current_stock = (db_inventory.current_stock or 0) + quantity_change
            self.db.commit()
            self.db.refresh(db_inventory)
        return db_inventory

    async def get_low_stock_items(self, threshold: int = 10) -> List[Inventory]:
        """Get items with stock below threshold"""
        return self.db.query(Inventory).filter(
            Inventory.current_stock <= threshold
        ).all()

    async def get_total_stock_by_virtual_type(self, virtual_type: int) -> int:
        """Calculate total stock for a virtual type"""
        inventory_items = await self.get_by_virtual_type(virtual_type)
        return sum(item.current_stock or 0 for item in inventory_items)

    async def delete(self, product_id: str) -> bool:
        """Delete inventory item"""
        db_inventory = await self.get_by_product_id(product_id)
        if db_inventory:
            self.db.delete(db_inventory)
            self.db.commit()
            return True
        return False
