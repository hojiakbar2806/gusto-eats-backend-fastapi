import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import models, database
from app.settings import settings
from app.utils import save_image, is_valid_image
from app.schemas import CategoryListResponse, CategoryResponse, UserResponse
from app.security import get_current_user

category_router = APIRouter(prefix="/categories", tags=['Categories'])


@category_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_category(name: str = Form(...), image: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: UserResponse = Depends(get_current_user)):
    if image and not is_valid_image(image):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image. Allowed types: jpeg, png. Max size: 5 MB",)

    file_location = save_image(
        image, name=name, dir=settings.CATEGORY_DIR)

    db_category = models.Category(
        name=name,
        image_path="/"+file_location
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": f"Category {db_category.id} successfully created"})


@category_router.get("/", response_model=CategoryListResponse, status_code=status.HTTP_200_OK)
async def get_categories(db: Session = Depends(database.get_db)):
    db_category = db.query(models.Category).all()
    return {"categories": db_category}


@category_router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(category_id: int, db: Session = Depends(database.get_db)):
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id).first()

    if not db_category:
        raise HTTPException(status_code=404, detail=f"Category {
                            category_id} not found")

    return db_category


@category_router.patch("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, name: str = Form(None), image: UploadFile = File(None), db: Session = Depends(database.get_db)):
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id).first()

    if not db_category:
        raise HTTPException(status_code=404, detail=f"Category {
                            category_id} not found")

    if name:
        db_category.name = name

    if image:
        os.makedirs(settings.CATEGORY_DIR, exist_ok=True)
        image_path = f"{
            settings.CATEGORY_DIR}/{db_category.name}_{image.filename}"

        with open(image_path, "wb") as file_object:
            shutil.copyfileobj(image.file, file_object)

        db_category.image_path = image_path

    db.commit()
    db.refresh(db_category)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Category {db_category.id} successfully updated"})


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: Session = Depends(database.get_db)):
    category_query = db.query(models.Category).filter(
        models.Category.id == category_id)
    db_category = category_query.first()

    if not db_category:
        raise HTTPException(status_code=404, detail=f"Category {
                            category_id} not found")

    if os.path.exists(db_category.image_path):
        os.remove(db_category.image_path)

    category_query.delete(synchronize_session=False)
    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Category {category_id} successfully deleted"})
