from fastapi import APIRouter
from models.discounts import Discount, DiscountCreate, DiscountModel
from repositories.discounts import DiscountRepositories
from services.discounts import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("/add", response_model=DiscountModel)
def create(discount: DiscountCreate):
    """
    Create a new discount.
    """
    return DiscountService.create(discount)

@router.delete("/delete/{discount_id}", response_model=DiscountModel)
def delete(discount_id: int):
    """
    Delete a discount by ID.
    """
    return DiscountService.delete(discount_id)