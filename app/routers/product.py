import os
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.settings import settings
from app.schemas import ProductResponse, ProductListResponse
from app.models import Product, Category
from app.utils import is_valid_image, save_image

product_router = APIRouter(prefix="/products", tags=['Products'])


@product_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    description: str = Form(default="No description"),
    type: str = Form(...),
    price: int = Form(...),
    discount: int = Form(default=0),
    count_in_stock: int = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if image and not is_valid_image(image):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image. Allowed types: jpeg, png. Max size: 5 MB",)

    db_category = db.query(Category).filter_by(id=category_id).first()

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_product = Product(
        name=name,
        description=description,
        type=type,
        price=price,
        discount=discount,
        count_in_stock=count_in_stock,
        category_id=category_id,
    )

    file_location = save_image(
        image, name=db_product.name, dir=settings.PRODUCT_DIR)
    db_product.image = file_location

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Product {db_product.id} successfully created"})


@product_router.get("/", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(Product).order_by(Product.total_review.desc()).all()
    return {"products": db_products}


@product_router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@product_router.patch("/{product_id}", status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    type: str = Form(None),
    price: int = Form(None),
    discount: int = Form(None),
    count_in_stock: int = Form(None),
    category_id: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):

    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name:
        db_product.name = name
    if description:
        db_product.description = description
    if type:
        db_product.type = type
    if price:
        db_product.price = price
    if discount:
        db_product.discount = discount
    if count_in_stock:
        db_product.count_in_stock = count_in_stock
    if category_id:
        db_category = db.query(Category).filter_by(id=category_id).first()
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_product.category_id = category_id
    if image:
        if not is_valid_image(image):
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image. Allowed types: jpeg, png. Max size: 5 MB",)
        file_location = save_image(
            image, name=db_product.name, dir=settings.PRODUCT_DIR)
        db_product.image = file_location

    db.commit()
    db.refresh(db_product)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Product {db_product.id} successfully update"})


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(
        Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if os.path.exists(db_product.image):
        os.remove(db_product.image)

    db.delete(db_product)
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Product {product_id} successfully deleted"})
