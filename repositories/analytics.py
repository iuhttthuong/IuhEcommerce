from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from models.analytics import Analytics, AnalyticsCreate, AnalyticsUpdate


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create(db: Session, analytics: AnalyticsCreate) -> Analytics:
        db_analytics = Analytics(**analytics.model_dump())
        db.add(db_analytics)
        db.commit()
        db.refresh(db_analytics)
        return db_analytics

    @staticmethod
    def get_by_id(db: Session, analytics_id: int) -> Optional[Analytics]:
        return db.query(Analytics).filter(Analytics.id == analytics_id).first()

    @staticmethod
    def get_by_shop(
        db: Session,
        shop_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        analytics_type: Optional[str] = None
    ) -> List[Analytics]:
        query = db.query(Analytics).filter(Analytics.shop_id == shop_id)
        
        if start_date:
            query = query.filter(Analytics.date >= start_date)
        if end_date:
            query = query.filter(Analytics.date <= end_date)
        if analytics_type:
            query = query.filter(Analytics.type == analytics_type)
            
        return query.order_by(Analytics.date.desc()).all()

    @staticmethod
    def update(db: Session, analytics_id: int, analytics: AnalyticsUpdate) -> Optional[Analytics]:
        db_analytics = db.query(Analytics).filter(Analytics.id == analytics_id).first()
        if db_analytics:
            for key, value in analytics.model_dump(exclude_unset=True).items():
                setattr(db_analytics, key, value)
            db.commit()
            db.refresh(db_analytics)
        return db_analytics

    @staticmethod
    def delete(db: Session, analytics_id: int) -> bool:
        db_analytics = db.query(Analytics).filter(Analytics.id == analytics_id).first()
        if db_analytics:
            db.delete(db_analytics)
            db.commit()
            return True
        return False

    @staticmethod
    def get_latest_analytics(db: Session, shop_id: int, analytics_type: str = "daily") -> Optional[Analytics]:
        return db.query(Analytics).filter(
            Analytics.shop_id == shop_id,
            Analytics.type == analytics_type
        ).order_by(Analytics.date.desc()).first()

    @staticmethod
    def get_analytics_summary(
        db: Session,
        shop_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get aggregated analytics data for a specific period"""
        analytics = db.query(Analytics).filter(
            Analytics.shop_id == shop_id,
            Analytics.date.between(start_date, end_date)
        ).all()
        
        if not analytics:
            return {}
            
        # Aggregate metrics from all analytics records
        summary = {
            "sales": {
                "total_sales": 0.0,
                "total_orders": 0,
                "average_order_value": 0.0,
                "conversion_rate": 0.0,
                "refund_rate": 0.0
            },
            "products": {
                "total_products": 0,
                "active_products": 0,
                "top_selling_products": {},
                "low_stock_products": {}
            },
            "customers": {
                "total_customers": 0,
                "new_customers": 0,
                "returning_customers": 0,
                "customer_satisfaction": 0.0
            },
            "marketing": {
                "total_promotions": 0,
                "active_promotions": 0,
                "promotion_effectiveness": {},
                "marketing_costs": 0.0,
                "marketing_roi": 0.0
            }
        }
        
        # Aggregate metrics
        for record in analytics:
            metrics = record.metrics
            for category in summary:
                if category in metrics:
                    for key, value in metrics[category].items():
                        if isinstance(value, (int, float)):
                            summary[category][key] += value
                        elif isinstance(value, dict):
                            if key not in summary[category]:
                                summary[category][key] = {}
                            for k, v in value.items():
                                if k in summary[category][key]:
                                    summary[category][key][k] += v
                                else:
                                    summary[category][key][k] = v
        
        # Calculate averages
        count = len(analytics)
        if count > 0:
            for category in summary:
                for key, value in summary[category].items():
                    if isinstance(value, (int, float)) and key.startswith("average"):
                        summary[category][key] = value / count
        
        return summary 