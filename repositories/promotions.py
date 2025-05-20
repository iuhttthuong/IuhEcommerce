from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.promotions import Promotion, PromotionCreate, PromotionUpdate


class PromotionRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create(db: Session, promotion: PromotionCreate) -> Promotion:
        db_promotion = Promotion(**promotion.model_dump())
        db.add(db_promotion)
        db.commit()
        db.refresh(db_promotion)
        return db_promotion

    @staticmethod
    def get_by_id(db: Session, promotion_id: int) -> Optional[Promotion]:
        return db.query(Promotion).filter(Promotion.id == promotion_id).first()

    @staticmethod
    def get_by_shop(db: Session, shop_id: int) -> List[Promotion]:
        return db.query(Promotion).filter(Promotion.shop_id == shop_id).all()

    @staticmethod
    def get_active(db: Session, shop_id: int) -> List[Promotion]:
        return db.query(Promotion).filter(
            Promotion.shop_id == shop_id,
            Promotion.is_active == True
        ).all()

    @staticmethod
    def update(db: Session, promotion_id: int, promotion: PromotionUpdate) -> Optional[Promotion]:
        db_promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if db_promotion:
            for key, value in promotion.model_dump(exclude_unset=True).items():
                setattr(db_promotion, key, value)
            db.commit()
            db.refresh(db_promotion)
        return db_promotion

    @staticmethod
    def delete(db: Session, promotion_id: int) -> bool:
        db_promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if db_promotion:
            db.delete(db_promotion)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Promotion]:
        return db.query(Promotion).filter(Promotion.code == code).first()

    @staticmethod
    def get_by_product(db: Session, product_id: int) -> List[Promotion]:
        return db.query(Promotion).filter(Promotion.product_id == product_id).all()

    @staticmethod
    def get_by_category(db: Session, category_id: int) -> List[Promotion]:
        return db.query(Promotion).filter(Promotion.category_id == category_id).all() 