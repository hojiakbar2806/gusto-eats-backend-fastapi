import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user
from app.schemas import UserResponse, ReviewResponse, ReviewCreate
from app.models import Product, Review

review_router = APIRouter(prefix="/review", tags=['Products Review'])


@review_router.post("/", response_model=ReviewResponse)
def create_review_for_product(review: ReviewCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_product = db.query(Product).filter(Product.id == review.product_id).first()
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin user can't add rewiev")
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id, Review.product_id == review.product_id).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You have already submitted a review for this product"
        )

    if review.rating < 0 or review.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 0 and 5"
        )

    db_product.total_review += 1

    db_review = Review(
        name=review.name,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
        user_id=current_user.id
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    reviews = db.query(Review).filter(Review.product_id == review.product_id).all()
    if reviews:
        total_rating = sum([r.rating for r in reviews])
        avg_rating = round(total_rating / len(reviews), 3)
        db_product.average_rating = avg_rating
        db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Review successfully created"})
