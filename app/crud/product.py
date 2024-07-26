import os
from typing import Optional

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import Product


async def get_all_products(db: AsyncSession):
    db_products = await db.execute(
        select(Product).options(selectinload(Product.category), selectinload(Product.reviews))
    )
    return db_products.scalars().all()


async def get_product(product_id: int, db: AsyncSession) -> Optional[Product]:
    db_product = await db.execute(
        select(Product).options(selectinload(Product.category), selectinload(Product.reviews)).where(
            Product.id == product_id)
    )
    return db_product.scalar_one_or_none()


async def get_top_rated_products(db: AsyncSession):
    db_products = await db.execute(
        select(Product).order_by(desc(Product.average_rating)).options(selectinload(Product.category),
                                                                       selectinload(Product.reviews))
    )
    return db_products.scalars().all()


async def delete_product(product_id: int, db: AsyncSession) -> JSONResponse:
    async with db.begin():
        db_product = await db.execute(select(Product).where(Product.id == product_id))
        db_product = db_product.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")

        if db_product.image and os.path.exists(os.path.join(settings.PRODUCT_DIR, db_product.image)):
            os.remove(os.path.join(settings.PRODUCT_DIR, db_product.image))

        db.delete(db_product)
        await db.commit()

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={"message": f"Mahsulot {product_id} muvaffaqiyatli o'chirildi"})
