from repositories.reviews import ReviewRepository
from models.reviews import ReviewCreatePayload, ReviewModel, ReviewUpdatePayload

class ReviewService:
    @staticmethod
    def create_review(payload: ReviewCreatePayload) -> ReviewModel:
        return ReviewRepository.create(payload)

    @staticmethod
    def get_review(review_id: int) -> ReviewModel:
        return ReviewRepository.get_one(review_id)

    @staticmethod
    def update_review(review_id: int, data: ReviewUpdatePayload) -> ReviewModel:
        return ReviewRepository.update(review_id, data)

    @staticmethod
    def delete_review(review_id: int) -> None:
        return ReviewRepository.delete(review_id)
    @staticmethod
    def get_reviews_by_product(product_id: int) -> list[ReviewModel]:
        return ReviewRepository.get_reviews_by_product(product_id)