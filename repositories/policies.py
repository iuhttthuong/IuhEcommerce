from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from models.policies import Policy, PolicyCreate, PolicyUpdate


class PolicyRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create(db: Session, policy: PolicyCreate) -> Policy:
        db_policy = Policy(**policy.model_dump())
        db.add(db_policy)
        db.commit()
        db.refresh(db_policy)
        return db_policy

    @staticmethod
    def get_by_id(db: Session, policy_id: int) -> Optional[Policy]:
        return db.query(Policy).filter(Policy.id == policy_id).first()

    @staticmethod
    def get_by_shop(
        db: Session,
        shop_id: int,
        policy_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Policy]:
        query = db.query(Policy).filter(Policy.shop_id == shop_id)
        
        if policy_type:
            query = query.filter(Policy.type == policy_type)
        if is_active is not None:
            query = query.filter(Policy.is_active == is_active)
            
        return query.order_by(Policy.created_at.desc()).all()

    @staticmethod
    def update(db: Session, policy_id: int, policy: PolicyUpdate) -> Optional[Policy]:
        db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if db_policy:
            for key, value in policy.model_dump(exclude_unset=True).items():
                setattr(db_policy, key, value)
            db.commit()
            db.refresh(db_policy)
        return db_policy

    @staticmethod
    def delete(db: Session, policy_id: int) -> bool:
        db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if db_policy:
            db.delete(db_policy)
            db.commit()
            return True
        return False

    @staticmethod
    def get_active_policies(
        db: Session,
        shop_id: int,
        policy_type: Optional[str] = None
    ) -> List[Policy]:
        """Get all active policies for a shop"""
        query = db.query(Policy).filter(
            Policy.shop_id == shop_id,
            Policy.is_active == True
        )
        
        if policy_type:
            query = query.filter(Policy.type == policy_type)
            
        return query.order_by(Policy.created_at.desc()).all()

    @staticmethod
    def get_policy_by_type(
        db: Session,
        shop_id: int,
        policy_type: str
    ) -> Optional[Policy]:
        """Get the active policy of a specific type for a shop"""
        return db.query(Policy).filter(
            Policy.shop_id == shop_id,
            Policy.type == policy_type,
            Policy.is_active == True
        ).first()

    @staticmethod
    def deactivate_policy(db: Session, policy_id: int) -> bool:
        """Deactivate a policy"""
        db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if db_policy:
            db_policy.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def get_policy_history(
        db: Session,
        shop_id: int,
        policy_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Policy]:
        """Get policy history for a shop"""
        query = db.query(Policy).filter(Policy.shop_id == shop_id)
        
        if policy_type:
            query = query.filter(Policy.type == policy_type)
            
        return query.order_by(Policy.created_at.desc()).limit(limit).all() 