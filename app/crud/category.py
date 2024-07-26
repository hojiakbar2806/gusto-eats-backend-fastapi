from fastapi import status, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models
from app.core.config import settings
from app.models import Product
from app.utils import is_valid_image, save_image

async def create_product(
        name: str,
        description: str,
        type: str,
        price: int,
        discount: int,
        count_in_stock: int,
        category_id: int,
        image: UploadFile,
        db: AsyncSession,
) -> Product:
    if image and not is_valid_image(image):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Noto'g'ri rasm. Ruxsat etilgan turlar: jpeg, png. Maksimal hajmi: 5 MB")

    db_category = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    db_category = db_category.scalar_one_or_none()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategoriya topilmadi")

    file_location = save_image(image, name=name, dir=settings.PRODUCT_DIR)
    db_product = Product(
        name=name,
        description=description,
        type=type,
        price=price,
        discount=discount,
        count_in_stock=count_in_stock,
        category_id=category_id,
        image_path=file_location
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


async def get_categories(db: AsyncSession):
    async with db.begin():
        result = await db.execute(select(models.Category))
        return result.scalars().all()


async def get_category(db: AsyncSession, category_id: int):
    async with db.begin():
        result = await db.execute(select(models.Category).where(models.Category.id == category_id))
        return result.scalars().first()


async def update_category(db: AsyncSession, category_id: int, name: str = None, image_path: str = None):
    async with db.begin():
        db_category = await db.get(models.Category, category_id)
        if db_category:
            if name:
                db_category.name = name
            if image_path:
                db_category.image_path = image_path
            await db.commit()
            await db.refresh(db_category)
        return db_category


async def delete_category(db: AsyncSession, category_id: int):
    async with db.begin():
        db_category = await db.get(models.Category, category_id)
        if db_category:
            db.delete(db_category)
            await db.commit()
            return True
        return False
