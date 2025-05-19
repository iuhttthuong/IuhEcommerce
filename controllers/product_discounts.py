from fastapi import APIRouter
from models.product_discounts import ProductDiscount, ProductDiscountCreate, ProductDiscountModel
from services.product_discounts import ProductDiscountService

router = APIRouter(prefix="/product_discounts", tags=["product_discounts"])
@router.post("/add", response_model=ProductDiscountModel)
def create(discount: ProductDiscountCreate):
    """
    Create a new product discount.
    """
    return ProductDiscountService.create(discount)
@router.delete("/delete/{discount_id}", response_model=ProductDiscountModel)
def delete(id: int):
    """
    Delete a product discount by ID.
    """
    return ProductDiscountService.delete(id)