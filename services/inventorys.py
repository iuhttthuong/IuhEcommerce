from models.inventories import Inventory, InventoryCreate
from repositories.inventories import InventoryRepositories

class InventoryService:
    @staticmethod
    def create(payload : InventoryCreate) -> Inventory:
        return InventoryRepositories.create(payload)