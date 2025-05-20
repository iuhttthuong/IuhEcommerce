from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from models.customer_service import CustomerService, CustomerServiceCreate, CustomerServiceUpdate


class CustomerServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create(db: Session, customer_service: CustomerServiceCreate) -> CustomerService:
        db_customer_service = CustomerService(**customer_service.model_dump())
        db.add(db_customer_service)
        db.commit()
        db.refresh(db_customer_service)
        return db_customer_service

    @staticmethod
    def get_by_id(db: Session, customer_service_id: int) -> Optional[CustomerService]:
        return db.query(CustomerService).filter(CustomerService.id == customer_service_id).first()

    @staticmethod
    def get_by_shop(
        db: Session,
        shop_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[CustomerService]:
        query = db.query(CustomerService).filter(CustomerService.shop_id == shop_id)
        
        if start_date:
            query = query.filter(CustomerService.created_at >= start_date)
        if end_date:
            query = query.filter(CustomerService.created_at <= end_date)
        if status:
            query = query.filter(CustomerService.status == status)
            
        return query.order_by(CustomerService.created_at.desc()).all()

    @staticmethod
    def update(db: Session, customer_service_id: int, customer_service: CustomerServiceUpdate) -> Optional[CustomerService]:
        db_customer_service = db.query(CustomerService).filter(CustomerService.id == customer_service_id).first()
        if db_customer_service:
            for key, value in customer_service.model_dump(exclude_unset=True).items():
                setattr(db_customer_service, key, value)
            db.commit()
            db.refresh(db_customer_service)
        return db_customer_service

    @staticmethod
    def delete(db: Session, customer_service_id: int) -> bool:
        db_customer_service = db.query(CustomerService).filter(CustomerService.id == customer_service_id).first()
        if db_customer_service:
            db.delete(db_customer_service)
            db.commit()
            return True
        return False

    @staticmethod
    def get_customer_service_stats(
        db: Session,
        shop_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get customer service statistics for a specific period"""
        query = db.query(CustomerService).filter(
            CustomerService.shop_id == shop_id,
            CustomerService.created_at.between(start_date, end_date)
        )
        
        total_tickets = query.count()
        resolved_tickets = query.filter(CustomerService.status == "resolved").count()
        pending_tickets = query.filter(CustomerService.status == "pending").count()
        avg_response_time = db.query(
            func.avg(CustomerService.response_time)
        ).filter(
            CustomerService.shop_id == shop_id,
            CustomerService.created_at.between(start_date, end_date),
            CustomerService.response_time.isnot(None)
        ).scalar() or 0
        
        return {
            "total_tickets": total_tickets,
            "resolved_tickets": resolved_tickets,
            "pending_tickets": pending_tickets,
            "resolution_rate": resolved_tickets / total_tickets if total_tickets > 0 else 0,
            "average_response_time": avg_response_time,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }

    @staticmethod
    def get_customer_service_history(
        db: Session,
        shop_id: int,
        limit: int = 10
    ) -> List[CustomerService]:
        """Get recent customer service history"""
        return db.query(CustomerService).filter(
            CustomerService.shop_id == shop_id
        ).order_by(
            CustomerService.created_at.desc()
        ).limit(limit).all() 