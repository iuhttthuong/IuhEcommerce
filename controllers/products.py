from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from db import get_db
from services.products import ProductServices
from models.products import ProductCreate, ProductResponse, ProductModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["products"]
)

@router.get("/home")
async def get_home_products(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get products for home page"""
    try:
        service = ProductServices(db)
        result = service.get_home_products(offset, limit)
        if not result:
            return {"total": 0, "products": []}
        return result
    except Exception as e:
        logger.error(f"Error getting home products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{query}", response_model=List[ProductResponse])
async def search_products(
    query: str,
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Search products by name or description"""
    service = ProductServices(db)
    return service.search(query, shop_id)

@router.get("/category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(
    category_id: str,
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get products by category"""
    service = ProductServices(db)
    return service.get_by_category(category_id, shop_id)

@router.get("/shop/{shop_id}", response_model=List[ProductResponse])
async def get_shop_products(
    shop_id: int,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get products by shop with optional filtering"""
    service = ProductServices(db)
    return service.get_by_shop(shop_id, skip, limit, category, search)

@router.get("/shop/{shop_id}/active", response_model=List[ProductResponse])
async def get_active_shop_products(
    shop_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get active products for a shop"""
    service = ProductServices(db)
    return service.get_active_products(shop_id, skip, limit)

@router.get("/shop/{shop_id}/stats")
async def get_shop_product_stats(
    shop_id: int,
    db: Session = Depends(get_db)
):
    """Get product statistics for a shop"""
    service = ProductServices(db)
    return service.get_product_stats(shop_id)

@router.post("", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    service = ProductServices(db)
    return service.create(product)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get a product by ID"""
    logger.info(f"Getting product with ID: {product_id}")
    try:
        service = ProductServices(db)
        product = service.get(product_id)
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        logger.info(f"Found product: {product.product_id} - {product.name}")
        return product
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    service = ProductServices(db)
    updated_product = service.update(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Delete a product"""
    service = ProductServices(db)
    if not service.delete(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.get("/{product_id}/info")
async def get_product_info(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed product information"""
    service = ProductServices(db)
    info = service.get_info(product_id)
    if not info:
        raise HTTPException(status_code=404, detail="Product not found")
    return info
