from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from models.finance import Finance, FinanceCreate, FinanceUpdate, TransactionType


class FinanceRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create(db: Session, finance: FinanceCreate) -> Finance:
        db_finance = Finance(**finance.model_dump())
        db.add(db_finance)
        db.commit()
        db.refresh(db_finance)
        return db_finance

    @staticmethod
    def get_by_id(db: Session, finance_id: int) -> Optional[Finance]:
        return db.query(Finance).filter(Finance.id == finance_id).first()

    @staticmethod
    def get_by_shop(db: Session, shop_id: int) -> List[Finance]:
        return db.query(Finance).filter(Finance.shop_id == shop_id).all()

    @staticmethod
    def get_by_order(db: Session, order_id: int) -> List[Finance]:
        return db.query(Finance).filter(Finance.order_id == order_id).all()

    @staticmethod
    def update(db: Session, finance_id: int, finance: FinanceUpdate) -> Optional[Finance]:
        db_finance = db.query(Finance).filter(Finance.id == finance_id).first()
        if db_finance:
            for key, value in finance.model_dump(exclude_unset=True).items():
                setattr(db_finance, key, value)
            db.commit()
            db.refresh(db_finance)
        return db_finance

    @staticmethod
    def delete(db: Session, finance_id: int) -> bool:
        db_finance = db.query(Finance).filter(Finance.id == finance_id).first()
        if db_finance:
            db.delete(db_finance)
            db.commit()
            return True
        return False

    @staticmethod
    def get_shop_balance(db: Session, shop_id: int) -> float:
        """Calculate current balance for a shop"""
        result = db.query(
            func.sum(Finance.amount).label('total')
        ).filter(
            Finance.shop_id == shop_id,
            Finance.status == 'completed'
        ).first()
        return result.total or 0.0

    @staticmethod
    def get_shop_transactions(
        db: Session,
        shop_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Finance]:
        """Get shop transactions with optional filters"""
        query = db.query(Finance).filter(Finance.shop_id == shop_id)
        
        if start_date:
            query = query.filter(Finance.transaction_date >= start_date)
        if end_date:
            query = query.filter(Finance.transaction_date <= end_date)
        if transaction_type:
            query = query.filter(Finance.type == transaction_type)
            
        return query.order_by(Finance.transaction_date.desc()).all()

    @staticmethod
    def get_shop_summary(
        db: Session,
        shop_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get financial summary for a shop"""
        query = db.query(
            Finance.type,
            func.sum(Finance.amount).label('total')
        ).filter(
            Finance.shop_id == shop_id,
            Finance.status == 'completed'
        )
        
        if start_date:
            query = query.filter(Finance.transaction_date >= start_date)
        if end_date:
            query = query.filter(Finance.transaction_date <= end_date)
            
        results = query.group_by(Finance.type).all()
        
        summary = {
            'income': 0.0,
            'expense': 0.0,
            'refund': 0.0,
            'withdrawal': 0.0,
            'deposit': 0.0
        }
        
        for type_, total in results:
            summary[type_] = total or 0.0
            
        return summary 