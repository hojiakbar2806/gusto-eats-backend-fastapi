from sqlalchemy.orm import Session
from app import models, schemas

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product_image(db: Session, product_id: int, file_path: str):
    db_image = models.ProductImage(product_id=product_id, file_path=file_path)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
