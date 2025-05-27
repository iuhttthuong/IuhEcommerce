from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from shop_chat.shop_manager import ShopManager
from models.products import ProductCreate
from models.orders import OrderCreate
from models.customers import CustomerCreate
from models.promotions import PromotionCreate
from shop_chat.schemas import AnalyticsRequest
from db import get_db

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get ShopManager instance
def get_shop_manager(db: Session = Depends(get_db)):
    return ShopManager(db)

# Chat related endpoints
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_shop(
    chat_message: ChatMessage,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Chat with shop assistant"""
    try:
        result = await shop_manager.process_chat_message(
            chat_message.message,
            chat_message.context or {},
            1
        )
        # Extract the assistant message if present, else fallback to a string
        assistant_message = result.get("message") if isinstance(result, dict) and "message" in result else str(result)
        return ChatResponse(response=assistant_message, context=chat_message.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Product related endpoints
@router.post("/products", response_model=Dict[str, Any])
async def create_product(
    product: ProductCreate,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Create a new product"""
    try:
        return await shop_manager.create_product(product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product(
    product_id: int,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Get product details"""
    try:
        return await shop_manager.get_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/products", response_model=List[Dict[str, Any]])
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """List all products with optional filters"""
    try:
        filters = {}
        if category:
            filters["category"] = category
        if min_price is not None:
            filters["min_price"] = min_price
        if max_price is not None:
            filters["max_price"] = max_price
        return await shop_manager.list_products(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Order related endpoints
@router.post("/orders", response_model=Dict[str, Any])
async def create_order(
    order: OrderCreate,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Create a new order"""
    try:
        return await shop_manager.create_order(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}", response_model=Dict[str, Any])
async def get_order(
    order_id: int,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Get order details"""
    try:
        return await shop_manager.get_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Analytics endpoints
@router.get("/analytics/summary", response_model=Dict[str, Any])
async def get_shop_summary(
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Get shop summary including key metrics"""
    try:
        return await shop_manager.get_shop_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    request: AnalyticsRequest,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Get detailed analytics"""
    try:
        return await shop_manager.get_analytics(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Marketing endpoints
@router.post("/marketing/campaigns", response_model=Dict[str, Any])
async def create_marketing_campaign(
    campaign: PromotionCreate,
    shop_manager: ShopManager = Depends(get_shop_manager)
):
    """Create a new marketing campaign"""
    try:
        return await shop_manager.create_marketing_campaign(campaign)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 