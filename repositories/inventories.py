
from models.inventories import Inventory, InventoryCreate
from db import Session
import numpy as np


class InventoryRepositories:
    @staticmethod
    def create(payload: InventoryCreate):
        with Session() as session:
            new_inventory = Inventory(**payload.model_dump())
            session.add(new_inventory)
            session.commit()
            session.refresh(new_inventory)
            
            return Inventory.validate(new_inventory)