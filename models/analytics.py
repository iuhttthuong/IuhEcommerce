from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base, TimestampMixin


class Analytics(Base, TimestampMixin):
    __tablename__ = "analytics"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    date: Mapped[datetime] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # daily, weekly, monthly
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # Store all metrics in JSON format
    
    # Relationships
    shop = relationship("Shop", back_populates="analytics")


class AnalyticsCreate(BaseModel):
    shop_id: int
    date: datetime
    type: str
    metrics: Dict[str, Any]


class AnalyticsUpdate(BaseModel):
    metrics: Dict[str, Any]


class AnalyticsResponse(BaseModel):
    id: int
    shop_id: int
    date: datetime
    type: str
    metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Pydantic models for specific analytics data
class SalesMetrics(BaseModel):
    total_sales: float
    total_orders: int
    average_order_value: float
    conversion_rate: float
    refund_rate: float


class ProductMetrics(BaseModel):
    total_products: int
    active_products: int
    top_selling_products: Dict[str, int]  # product_id: quantity
    low_stock_products: Dict[str, int]  # product_id: current_stock


class CustomerMetrics(BaseModel):
    total_customers: int
    new_customers: int
    returning_customers: int
    customer_satisfaction: float  # Average rating


class MarketingMetrics(BaseModel):
    total_promotions: int
    active_promotions: int
    promotion_effectiveness: Dict[str, float]  # promotion_id: conversion_rate
    marketing_costs: float
    marketing_roi: float


class ShopAnalytics(BaseModel):
    sales: SalesMetrics
    products: ProductMetrics
    customers: CustomerMetrics
    marketing: MarketingMetrics
    period: Dict[str, datetime]  # start_date, end_date 