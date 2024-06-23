from sqlalchemy.orm import Session
from app import models, schemas, security


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_phone_number(db: Session, phone_number: int):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_blacklist_token(db: Session, token: str):
    blacklisted_token = models.BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    db.refresh(blacklisted_token)
    return blacklisted_token


def is_token_blacklisted(db: Session, token: str) -> bool:
    blacklisted_token = db.query(
        models.BlacklistedToken).filter_by(token=token).first()
    return blacklisted_token is not None
