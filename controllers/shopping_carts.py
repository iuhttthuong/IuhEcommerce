from fastapi import APIRouter, HTTPException
from models.shopping_carts import ShoppingCart, ShoppingCartModel, ShoppingCartCreate
from services.shopping_carts import ShoppingCartService
from typing import List

router = APIRouter(prefix="/shopping_carts", tags=["shopping_carts"])
@router.post("/add", response_model=ShoppingCartModel)
def create(payload: ShoppingCartCreate):
    try:
        cart = ShoppingCartService.create(payload)
        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/get/{cart_id}", response_model=ShoppingCartModel)
def get(cart_id: int):
    try:
        cart = ShoppingCartService.get(cart_id)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/update/{cart_id}", response_model=ShoppingCartModel)
def update(cart_id: int, data: ShoppingCartCreate):
    try:
        cart = ShoppingCartService.update(cart_id, data)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/delete/{cart_id}")
def delete(cart_id: int):
    try:
        ShoppingCartService.delete(cart_id)
        return {"message": "Shopping cart deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_shopping_cart_by_customer_id/{customer_id}")
def get_shopping_cart_by_customer_id(customer_id: int) -> list[ShoppingCartModel]:
    """
    Get shopping cart by customer ID    
    """
    try:
        cart = ShoppingCartService.get_shopping_cart_by_customer_id(customer_id)
        if not cart:
            raise HTTPException(status_code=404, detail="Shopping cart not found")
        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    print(get_shopping_cart_by_customer_id(1) )
main()