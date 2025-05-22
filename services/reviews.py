from repositories.reviews import ReviewRepository
from models.reviews import ReviewCreate, ReviewUpdate, ReviewResponse
from loguru import logger

class ReviewService:
    @staticmethod
    def create_review(payload: ReviewCreate) -> ReviewResponse:
        try:
            review = ReviewRepository.create(payload)
            return ReviewResponse.model_validate(review)
        except Exception as e:
            logger.error(f"Error in create_review service: {e}")
            raise

    @staticmethod
    def get_review(review_id: int) -> ReviewResponse:
        try:
            review = ReviewRepository.get_by_id(review_id)
            if not review:
                return None
            return ReviewResponse.model_validate(review)
        except Exception as e:
            logger.error(f"Error in get_review service: {e}")
            raise

    @staticmethod
    def update_review(review_id: int, payload: ReviewUpdate) -> ReviewResponse:
        try:
            review = ReviewRepository.update(review_id, payload)
            if not review:
                return None
            return ReviewResponse.model_validate(review)
        except Exception as e:
            logger.error(f"Error in update_review service: {e}")
            raise

    @staticmethod
    def delete_review(review_id: int) -> bool:
        try:
            ReviewRepository.delete(review_id)
            return True
        except Exception as e:
            logger.error(f"Error in delete_review service: {e}")
            raise

    @staticmethod
    def get_reviews_by_product(product_id: int) -> list[ReviewResponse]:
        try:
            reviews = ReviewRepository.get_by_product_id(product_id)
            return [ReviewResponse.model_validate(review) for review in reviews]
        except Exception as e:
            logger.error(f"Error in get_reviews_by_product service: {e}")
            raise