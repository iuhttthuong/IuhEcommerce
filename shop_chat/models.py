from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ShopBase(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ShopCreate(ShopBase):
    pass

class ShopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ShopResponse(ShopBase):
    id: int
    rating: float = 0.0
    total_products: int = 0
    total_orders: int = 0
    total_revenue: float = 0.0

    class Config:
        from_attributes = True

class ShopStats(BaseModel):
    total_products: int
    total_orders: int
    total_revenue: float
    average_rating: float
    monthly_sales: Dict[str, float]
    top_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]

class ShopSettings(BaseModel):
    auto_confirm_orders: bool = False
    notification_preferences: Dict[str, bool] = {
        "new_order": True,
        "low_stock": True,
        "customer_review": True,
        "payment_received": True
    }
    shipping_options: List[str] = []
    payment_methods: List[str] = []
    business_hours: Dict[str, List[str]] = {}
    return_policy: Optional[str] = None
    shipping_policy: Optional[str] = None 