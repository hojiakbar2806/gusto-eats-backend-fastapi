from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.db.base import get_async_session
from app.models import Product, Review
from app.schemas import ReviewCreate, ReviewResponse, UserResponse

review_router = APIRouter(prefix="/review", tags=['Mahsulotlar Sharhi'])


@review_router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review_for_product(
        review: ReviewCreate,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserResponse = Depends(get_current_user)
) -> JSONResponse:
    # Joriy foydalanuvchi admin emasligini tekshirish
    if current_user.is_staff or current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin foydalanuvchilar sharh qoldirolmaydi")

    db_product = await db.execute(select(Product).where(Product.id == review.product_id))
    db_product = db_product.scalar_one_or_none()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")

    # Foydalanuvchi mahsulotga sharh qoldirganligini tekshirish
    existing_review = await db.execute(select(Review).where(
        Review.user_id == current_user.id,
        Review.product_id == review.product_id
    ))
    existing_review = existing_review.scalar_one_or_none()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Siz bu mahsulot uchun sharh qoldirgansiz")

    # Reytingni tekshirish
    if review.rating < 0 or review.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reyting 0 dan 5 gacha bo'lishi kerak")

    # Mahsulot uchun umumiy sharhlar sonini yangilash
    db_product.total_review += 1

    # Sharhni yaratish va ma'lumotlar bazasiga qo'shish
    db_review = Review(
        name=review.name,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
        user_id=current_user.id
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    # Mahsulot uchun o'rtacha reytingni hisoblash va yangilash
    reviews = await db.execute(select(Review).where(Review.product_id == review.product_id))
    reviews = reviews.scalars().all()
    if reviews:
        total_rating = sum([r.rating for r in reviews])
        avg_rating = round(total_rating / len(reviews), 3)
        db_product.average_rating = avg_rating
        await db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Sharh muvaffaqiyatli yaratildi"})
