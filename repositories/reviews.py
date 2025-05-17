from db import Session
from models.reviews import Review, ReviewModel, ReviewCreatePayload, ReviewUpdatePayload

class ReviewRepository:
    @staticmethod
    def create(payload: ReviewCreatePayload) -> ReviewModel:
        with Session() as session:
            review = Review(**payload.model_dump())
            session.add(review)
            session.commit()
            session.refresh(review)
            return ReviewModel.model_validate(review)

    @staticmethod
    def get_one(review_id: int) -> ReviewModel:
        with Session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")
            return ReviewModel.model_validate(review)

    @staticmethod
    def update(review_id: int, data: ReviewUpdatePayload) -> ReviewModel:
        with Session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(review, field, value)

            session.commit()
            session.refresh(review)
            return ReviewModel.model_validate(review)

    @staticmethod
    def delete(review_id: int):
        with Session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")

            session.delete(review)
            session.commit()
    @staticmethod
    def get_reviews_by_product(product_id: int):
        with Session() as session:
            reviews = session.query(Review).filter(Review.product_id == product_id).all()
            if not reviews:
                raise ValueError(f"No reviews found for product ID {product_id}")
            return [ReviewModel.model_validate(review) for review in reviews]