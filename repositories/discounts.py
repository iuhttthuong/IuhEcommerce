from models.discounts import Discount, DiscountCreate, DiscountResponse, DiscountUpdate
from models.product_discounts import ProductDiscount
from db import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

class DiscountRepositories:
    @staticmethod
    def create(discount: DiscountCreate) -> Discount:
        db = Session()
        try:
            db_discount = Discount(**discount.model_dump())
            db.add(db_discount)
            db.commit()
            db.refresh(db_discount)
            return db_discount
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def get_by_id(discount_id: int) -> Optional[Discount]:
        db = Session()
        try:
            return db.query(Discount).filter(Discount.discount_id == discount_id).first()
        finally:
            db.close()

    @staticmethod
    def list_all() -> List[Discount]:
        db = Session()
        try:
            return db.query(Discount).all()
        finally:
            db.close()

    @staticmethod
    def update(discount_id: int, discount: DiscountUpdate) -> Optional[Discount]:
        db = Session()
        try:
            db_discount = db.query(Discount).filter(Discount.discount_id == discount_id).first()
            if db_discount:
                update_data = discount.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_discount, key, value)
                db.commit()
                db.refresh(db_discount)
            return db_discount
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def delete(discount_id: int) -> bool:
        db = Session()
        try:
            # First delete all associated product_discounts records
            db.query(ProductDiscount).filter(ProductDiscount.discount_id == discount_id).delete()
            
            # Then delete the discount
            db_discount = db.query(Discount).filter(Discount.discount_id == discount_id).first()
            if db_discount:
                db.delete(db_discount)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()