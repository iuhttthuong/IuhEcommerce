## ReviewController
# This file contains the ReviewController class, which handles the review-related operations.


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.reviews import Review, ReviewCreate, ReviewUpdate, ReviewResponse
from repositories.reviews import ReviewRepositories
from db import get_db

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    try:
        review_repo = ReviewRepositories(db)
        db_review = review_repo.create(review.model_dump())
        return db_review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review_repo = ReviewRepositories(db)
    review = review_repo.get_by_id(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(review_id: int, review: ReviewUpdate, db: Session = Depends(get_db)):
    review_repo = ReviewRepositories(db)
    db_review = review_repo.update(review_id, review.model_dump(exclude_unset=True))
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review_repo = ReviewRepositories(db)
    if not review_repo.delete(review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    review_repo = ReviewRepositories(db)
    reviews = review_repo.get_by_product(product_id)
    return reviews