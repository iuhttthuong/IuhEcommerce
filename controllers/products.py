from fastapi import APIRouter
from models.products import Product, ProductModel, ProductCreate
from services.products import ProductServices

router = APIRouter(tags=["products"])
@router.post("/add", response_model=ProductModel)
def create(product: ProductCreate):
    """
    Create a new product.
    """
    return ProductServices.create(product)
@router.delete("/delete/{product_id}", response_model=ProductModel)
def delete(product_id: int):
    """
    Delete a product by ID.
    """
    return ProductServices.delete(product_id)
@router.get("/get/{product_id}", response_model=ProductModel)
def get(product_id: int):
    """
    Get a product by ID.
    """
    return ProductServices.get(product_id)
@router.put("/update/{product_id}", response_model=ProductModel)
def update(product_id: int, product: ProductCreate):
    """
    Update a product by ID.
    """
    return ProductServices.update(product_id, product)
@router.get("/get_info/{id}")
def get_info(id: int):
    """
    Get product information by ID.
    """
    return ProductServices.get_info(id)
@router.get("/get_home_products")
def get_home_products(offset: int = 0, limit: int = 10):
    """
    Get home products with pagination.
    """
    return ProductServices.get_home_products(offset, limit)