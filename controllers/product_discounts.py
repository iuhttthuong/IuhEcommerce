from fastapi import APIRouter
from models.product_discounts import ProductDiscount, ProductDiscountCreate, ProductDiscountModel
from services.product_discounts import ProductDiscountService

router = APIRouter(prefix="/product_discounts", tags=["product_discounts"])

@router.post("/add", response_model=ProductDiscountModel)
def create(product_discount: ProductDiscountCreate):
    """
    Create a new product discount.
    """
    return ProductDiscountService.create(product_discount)

@router.delete("/delete/{product_id}/{discount_id}", response_model=ProductDiscountModel)
def delete(product_id: int, discount_id: int):
    """
    Delete a product discount by product_id and discount_id.
    """
    return ProductDiscountService.delete(product_id, discount_id)

@router.get("/get/{product_id}/{discount_id}", response_model=ProductDiscountModel)
def get(product_id: int, discount_id: int):
    """
    Get a product discount by product_id and discount_id.
    """
    return ProductDiscountService.get(product_id, discount_id)

@router.put("/update/{product_id}/{discount_id}", response_model=ProductDiscountModel)
def update(product_id: int, discount_id: int, product_discount: ProductDiscountCreate):
    """
    Update a product discount by product_id and discount_id.
    """
    return ProductDiscountService.update(product_id, discount_id, product_discount)