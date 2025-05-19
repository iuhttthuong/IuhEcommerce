from db import Session
from models.reviews import Review, ReviewCreate, ReviewUpdate
from models.products import Product
from models.customers import Customer
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any

class ReviewRepositories:
    @staticmethod
    def create(review: ReviewCreate) -> Review:
        with Session() as session:
            review = Review(**review.model_dump())
            session.add(review)
            session.commit()
            session.refresh(review)
            return review
    
    @staticmethod
    def get_by_id(review_id: int) -> Review:
        with Session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")
            return review
    
    @staticmethod
    def get_by_product_id(product_id: int) -> list[Review]:
        with Session() as session:
            reviews = session.query(Review).filter(Review.product_id == product_id).all()
            return reviews
    
    @staticmethod
    def get_by_customer_id(customer_id: int) -> list[Review]:
        with Session() as session:
            reviews = session.query(Review).filter(Review.customer_id == customer_id).all()
            return reviews
    
    @staticmethod
    def update(review_id: int, data: ReviewUpdate) -> Review:
        with Session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(review, field, value)

            session.commit()
            session.refresh(review)
            return review
    
    @staticmethod
    def delete(review_id: int):
        with Session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")

            session.delete(review)
            session.commit()

    @staticmethod
    def get_product_reviews(product_id: int):
        with Session() as session:
            reviews = session.query(Review).filter(Review.product_id == product_id).all()
            if not reviews:
                return []

            result = []
            for review in reviews:
                customer = session.get(Customer, review.customer_id)
                review_data = {
                    "review": review,
                    "customer": customer
                }
                result.append(review_data)
            return result 