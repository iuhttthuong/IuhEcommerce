from fastapi import APIRouter
from models.shops import Shop, ShopModel, ShopCreate
from services.shops import ShopServices

router = APIRouter(prefix="/shops", tags=["shops"])

@router.post("/add", response_model=ShopModel)
def create(shop: ShopCreate):
    """
    Create a new shop.
    """
    return ShopServices.create(shop)

@router.delete("/delete/{shop_id}", response_model=ShopModel)
def delete(shop_id: int):
    """
    Delete a shop by ID.
    """
    return ShopServices.delete(shop_id)

@router.get("/get/{shop_id}", response_model=ShopModel)
def get(shop_id: int):
    """
    Get a shop by ID.
    """
    return ShopServices.get(shop_id)

@router.put("/update/{shop_id}", response_model=ShopModel)
def update(shop_id: int, shop: ShopCreate):
    """
    Update a shop by ID.
    """
    return ShopServices.update(shop_id, shop)

@router.get("/get_products/{shop_id}")
def get_shop_products(shop_id: int, offset: int = 0, limit: int = 10):
    """
    Get all products from a specific shop with pagination.
    """
    return ShopServices.get_shop_products(shop_id, offset, limit)

@router.get("/get_stats/{shop_id}")
def get_shop_stats(shop_id: int):
    """
    Get shop statistics including total products, total sales, etc.
    """
    return ShopServices.get_shop_stats(shop_id)

@router.get("/search")
def search_shops(query: str, offset: int = 0, limit: int = 10):
    """
    Search shops by name or description.
    """
    return ShopServices.search_shops(query, offset, limit)

@router.get("/get_top_shops")
def get_top_shops(limit: int = 10):
    """
    Get top performing shops based on sales and ratings.
    """
    return ShopServices.get_top_shops(limit) 