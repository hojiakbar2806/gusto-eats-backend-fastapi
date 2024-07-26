from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.helper import clean_string
from app.core.config import settings
from app.core.security import get_current_user
from app.crud import get_categories, get_category, delete_category
from app.db.base import get_async_session
from app.models import Category
from app.schemas import CategoryListResponse, CategoryResponse, UserResponse
from app.utils import save_image, is_valid_image

category_router = APIRouter(prefix="/categories", tags=['Categories'])


@category_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_category_api(
        name: str = Form(...),
        image: UploadFile = File(...),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserResponse = Depends(get_current_user)
):
    if not is_valid_image(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noto'g'ri rasm. Ruxsat etilgan turlari: jpeg, png. Maksimal hajmi: 5 MB"
        )

    file_location = await save_image(image, name=name, dir=settings.CATEGORY_DIR)

    db_category = Category(
        name=clean_string(name),
        image_path=file_location
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Kategoriya {db_category.id} muvaffaqiyatli yaratildi"}
    )


@category_router.get("/", response_model=CategoryListResponse, status_code=status.HTTP_200_OK)
async def get_categories_api(db: AsyncSession = Depends(get_async_session)):
    db_categories = await get_categories(db)
    return {"categories": db_categories}


@category_router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category_api(category_id: int, db: AsyncSession = Depends(get_async_session)):
    db_category = await get_category(db, category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kategoriya {category_id} topilmadi"
        )
    return db_category


@category_router.patch("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category_api(
        category_id: int,
        name: str = Form(None),
        image: UploadFile = File(None),
        db: AsyncSession = Depends(get_async_session)
):
    db_category = await get_category(db, category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kategoriya {category_id} topilmadi"
        )

    if image:
        if not is_valid_image(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Noto'g'ri rasm. Ruxsat etilgan turlari: jpeg, png. Maksimal hajmi: 5 MB"
            )
        file_location = await save_image(image, name=db_category.name, dir=settings.CATEGORY_DIR)
        db_category.image_path = file_location

    if name:
        db_category.name = clean_string(name)

    await db.commit()
    await db.refresh(db_category)

    return db_category


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_api(category_id: int, db: AsyncSession = Depends(get_async_session)):
    success = await delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kategoriya {category_id} topilmadi"
        )
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": f"Kategoriya {category_id} muvaffaqiyatli o'chirildi"}
    )
