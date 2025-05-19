from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Schemas
class ShopCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int

class ShopUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ShopSettingsUpdateRequest(BaseModel):
    auto_confirm_orders: Optional[bool] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    shipping_options: Optional[List[str]] = None
    payment_methods: Optional[List[str]] = None
    business_hours: Optional[Dict[str, List[str]]] = None
    return_policy: Optional[str] = None
    shipping_policy: Optional[str] = None

class ShopSearchRequest(BaseModel):
    query: str
    limit: int = 10
    page: int = 1

class ShopStatsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Response Schemas
class ShopBasicResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    rating: float
    status: str
    created_at: datetime

class ShopDetailedResponse(ShopBasicResponse):
    total_products: int
    total_orders: int
    total_revenue: float
    owner_id: int
    updated_at: datetime

class ShopStatsResponse(BaseModel):
    total_products: int
    total_orders: int
    total_revenue: float
    average_rating: float
    monthly_sales: Dict[str, float]
    top_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]

class ShopSettingsResponse(BaseModel):
    auto_confirm_orders: bool
    notification_preferences: Dict[str, bool]
    shipping_options: List[str]
    payment_methods: List[str]
    business_hours: Dict[str, List[str]]
    return_policy: Optional[str]
    shipping_policy: Optional[str]

class ShopListResponse(BaseModel):
    shops: List[ShopBasicResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class ShopSearchResponse(BaseModel):
    results: List[ShopBasicResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationErrorResponse(ErrorResponse):
    field_errors: Dict[str, List[str]] 