from fastapi import APIRouter, HTTPException
from models.discounts import Discount, DiscountCreate, DiscountModel, DiscountUpdate
from services.discounts import DiscountService
from typing import List

router = APIRouter(prefix="/discounts", tags=["Discounts"])

@router.post("/", response_model=DiscountModel)
def create_discount(discount: DiscountCreate):
    return DiscountService.create_discount(discount)

@router.get("/{discount_id}", response_model=DiscountModel)
def get_discount(discount_id: int):
    discount = DiscountService.get_discount(discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount

@router.get("/", response_model=List[DiscountModel])
def list_discounts():
    return DiscountService.list_discounts()

@router.put("/{discount_id}", response_model=DiscountModel)
def update_discount(discount_id: int, discount: DiscountUpdate):
    updated_discount = DiscountService.update_discount(discount_id, discount)
    if not updated_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    return updated_discount

@router.delete("/{discount_id}")
def delete_discount(discount_id: int):
    success = DiscountService.delete_discount(discount_id)
    if not success:
        raise HTTPException(status_code=404, detail="Discount not found")
    return {"message": "Discount deleted successfully"}