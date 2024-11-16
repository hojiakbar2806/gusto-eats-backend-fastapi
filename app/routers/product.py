from aiogram.types import FSInputFile
from fastapi import APIRouter, Depends, Form, UploadFile, File, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.bot import bot
from app.bot.helper import clean_string
from app.core.config import settings
from app.core.security import get_current_user
from app.crud.product import get_all_products, get_product, delete_product, get_top_rated_products
from app.database.base import get_async_session
from app.database.models import Category, Product
from app.schemas import UserResponse, ProductListResponse, ProductResponse
from app.utils import is_valid_image, save_image

product_router = APIRouter(prefix="/products", tags=['Mahsulotlar'])


@product_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product_api(
        name: str = Form(...),
        description: str = Form(default="Tavsif yo'q"),
        type: str = Form(...),
        price: int = Form(...),
        discount: int = Form(default=0),
        count_in_stock: int = Form(...),
        category_id: int = Form(...),
        image: UploadFile = File(...),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserResponse = Depends(get_current_user)
):
    # Validate category
    db_category = await db.execute(select(Category).filter(Category.id == category_id))
    db_category = db_category.scalar_one_or_none()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategoriya topilmadi")

    # Validate image
    if not is_valid_image(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noto'g'ri rasm. Ruxsat etilgan turlari: jpeg, png. Maksimal hajmi: 5 MB"
        )

    # Save image
    file_location = await save_image(image, name=name, dir=settings.PRODUCT_DIR)

    # Calculate discounted price
    discounted_price = price - (price * discount / 100)

    # Create product
    db_product = Product(
        name=clean_string(name),
        description=clean_string(description),
        type=clean_string(type),
        price=discounted_price,
        discount=discount,
        count_in_stock=count_in_stock,
        category_id=category_id,
        image=file_location
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    # Send image to Telegram
    try:
        telegram_image = FSInputFile(path=db_product.image)
        response = await bot.send_photo(
            chat_id=settings.OWNER_ID, photo=telegram_image,
            caption=f"Mahsulot qo'shildi!!!\nMahsulot id: {db_product.id}\nMahsulot nomi: {db_product.name}"
        )
        file_id = response.photo[-1].file_id
        db_product.telegram_file_id = file_id
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Mahsulot yaratildi, lekin botda xatolik: {str(e)}"}
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Mahsulot {db_product.id} muvaffaqiyatli yaratildi"}
    )


@product_router.get("/", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_all_products_api(db: AsyncSession = Depends(get_async_session)):
    products = await get_all_products(db)
    return {"products": products}


@product_router.get("/view/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: AsyncSession = Depends(get_async_session)):
    db_product = await get_product(product_id, db)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")
    return db_product


@product_router.patch("/{product_id}", status_code=status.HTTP_200_OK)
async def update_product_api(
        product_id: int,
        name: str = Form(None),
        description: str = Form(None),
        type: str = Form(None),
        price: int = Form(None),
        discount: int = Form(None),
        count_in_stock: int = Form(None),
        category_id: int = Form(None),
        image: UploadFile = File(None),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserResponse = Depends(get_current_user)
):
    # Fetch the product
    db_product = await get_product(product_id, db)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")

    # Validate and update category if provided
    if category_id is not None:
        db_category = await db.execute(select(Category).filter(Category.id == category_id))
        db_category = db_category.scalar_one_or_none()
        if not db_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategoriya topilmadi")
        db_product.category_id = category_id

    # Update fields with provided values
    if name:
        db_product.name = clean_string(name)
    if description:
        db_product.description = clean_string(description)
    if type:
        db_product.type = clean_string(type)
    if price is not None:
        db_product.price = price
    if discount is not None:
        db_product.discount = discount
    if count_in_stock is not None:
        db_product.count_in_stock = count_in_stock

    # Recalculate discounted price if both price and discount are provided
    if price is not None and discount is not None:
        db_product.price = price - (price * discount / 100)

    # Handle image update
    if image:
        if not is_valid_image(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Noto'g'ri rasm. Ruxsat etilgan turlar: jpeg, png. Maksimal hajmi: 5 MB"
            )
        file_location = await save_image(image, name=db_product.name, dir=settings.PRODUCT_DIR)
        db_product.image = file_location

        # Send updated image to Telegram
        telegram_image = FSInputFile(path=file_location)
        response = await bot.send_photo(
            chat_id=settings.OWNER_ID, photo=telegram_image,
            caption=f"Mahsulot yangilandi!\nMahsulot id: {db_product.id}\nMahsulot nomi: {db_product.name}"
        )
        file_id = response.photo[-1].file_id
        db_product.telegram_file_id = file_id

    # Save changes to the database
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Mahsulot {db_product.id} muvaffaqiyatli yangilandi"}
    )


@product_router.get("/recommends", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_recommendation_products(db: AsyncSession = Depends(get_async_session)):
    products = await get_top_rated_products(db)
    return {"products": products}


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_api(product_id: int, db: AsyncSession = Depends(get_async_session)):
    success = await delete_product(product_id, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Mahsulot muvaffaqiyatli o'chirildi"}
    )
