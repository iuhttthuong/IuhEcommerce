from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.reviews import Review, ReviewCreate, ReviewUpdate, ReviewResponse
from loguru import logger

class ReviewRepositories:
    def __init__(self, db: Session):
        self.db = db

    def create(self, review_data: dict) -> Optional[Review]:
        try:
            db_review = Review(**review_data)
            self.db.add(db_review)
            self.db.commit()
            self.db.refresh(db_review)
            return db_review
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error creating review: {str(e)}")
            if "reviews_product_id_fkey" in str(e):
                raise ValueError("Product does not exist")
            elif "reviews_customer_id_fkey" in str(e):
                raise ValueError("Customer does not exist")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating review: {str(e)}")
            raise

    def get_by_id(self, review_id: int) -> Optional[Review]:
        try:
            return self.db.query(Review).filter(Review.review_id == review_id).first()
        except Exception as e:
            logger.error(f"Error getting review by id: {str(e)}")
            raise

    def get_by_product(self, product_id: int) -> List[Review]:
        try:
            # Use distinct() to handle joined eager loading
            return self.db.query(Review).filter(
                Review.product_id == product_id
            ).distinct().all()
        except Exception as e:
            logger.error(f"Error getting reviews by product: {str(e)}")
            raise

    def get_by_customer(self, customer_id: int) -> List[Review]:
        try:
            stmt = select(Review).where(Review.customer_id == customer_id)
            return list(self.db.execute(stmt).scalars().all())
        except Exception as e:
            logger.error(f"Error getting reviews by customer: {str(e)}")
            raise

    def get_all(self) -> List[Review]:
        try:
            return self.db.query(Review).all()
        except Exception as e:
            logger.error(f"Error getting all reviews: {str(e)}")
            raise

    def update(self, review_id: int, review_data: dict) -> Optional[Review]:
        try:
            review = self.get_by_id(review_id)
            if review:
                for key, value in review_data.items():
                    setattr(review, key, value)
                self.db.commit()
                self.db.refresh(review)
            return review
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating review: {str(e)}")
            raise

    def delete(self, review_id: int) -> bool:
        try:
            review = self.get_by_id(review_id)
            if review:
                self.db.delete(review)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting review: {str(e)}")
            raise