## ReviewController
# This file contains the ReviewController class, which handles the review-related operations.


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List
from models.reviews import ReviewCreatePayload, ReviewUpdatePayload, ReviewDeletePayload
from services.reviews import ReviewService


router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/add", response_model=ReviewCreatePayload)
def create_review(payload: ReviewCreatePayload):
    try:
        review = ReviewService.create_review(payload)
        return JSONResponse(status_code=201, content=jsonable_encoder(review))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/get/{review_id}", response_model=ReviewCreatePayload)
def get_review(review_id: int):
    try:
        review = ReviewService.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return JSONResponse(status_code=200, content=jsonable_encoder(review))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/update/{review_id}", response_model=ReviewUpdatePayload)    
def update_review(review_id: int, payload: ReviewUpdatePayload):
    try:
        review = ReviewService.update_review(review_id, payload)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return JSONResponse(status_code=200, content=jsonable_encoder(review))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.delete("/delete/{review_id}", response_model=ReviewDeletePayload)
def delete_review(review_id: int):
    try:
        ReviewService.delete_review(review_id)
        return JSONResponse(status_code=204, content={"message": "Review deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/get_reviews_by_product/{product_id}", response_model=List[ReviewCreatePayload])
def get_reviews_by_product(product_id: int):
    try:
        reviews = ReviewService.get_reviews_by_product(product_id)
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this product")
        return JSONResponse(status_code=200, content=jsonable_encoder(reviews))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))