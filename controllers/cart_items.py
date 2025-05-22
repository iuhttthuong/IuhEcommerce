from fastapi import APIRouter, HTTPException
from models.cart_items import CartItemCreate, CartItemModel 
from services.cart_items import CartItemService

router = APIRouter(prefix="/cart_items", tags=["Cart Items"])
@router.post("/add", response_model=CartItemModel)
def create(cart_item: CartItemCreate):
    return CartItemService.create(cart_item)
@router.get("/get{cart_id}/{product_id}", response_model=CartItemModel)
def get(cart_id: int, product_id: int):
    cart_item = CartItemService.get(cart_id, product_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart_item
@router.put("/update/{cart_id}/{product_id}", response_model=CartItemModel)
def update(cart_id: int, product_id: int, quantity: int):
    cart_item = CartItemService.update(cart_id, product_id, quantity)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart_item
@router.delete("/delete/{cart_id}/{product_id}")
def delete(cart_id: int, product_id: int):
    CartItemService.delete(cart_id, product_id)
    return {"message": "Cart item deleted successfully"}
@router.get("/{cart_id}", response_model=list[CartItemModel])
def get_cart_items_by_cart_id(cart_id: int) -> list[CartItemModel]:
    cart_items = CartItemService.get_cart_items_by_cart_id(cart_id)
    if not cart_items:
        raise HTTPException(status_code=404, detail="No cart items found")
    return cart_items

