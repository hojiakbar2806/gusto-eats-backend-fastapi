from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db
from app.settings import settings
from app.schemas import UserCreate, UserResponse, UserListResponse, UserUpdate
from app.security import get_current_user, get_password_hash


user_router = APIRouter(prefix="/users", tags=['Users'])


@user_router.post("/create", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")

    exist_user = db.query(User).filter(
        User.phone_number == user.phone_number).first()
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=False,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return JSONResponse(content={"message": "User successfully registered"}, status_code=status.HTTP_201_CREATED)


@user_router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    db_users = db.query(User).order_by(User.id).offset(skip).limit(limit).all()
    return {"users": db_users}


@user_router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != db_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")

    return db_user


@user_router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.phone_number:
        db_user.phone_number = user_update.phone_number
    if user_update.password:
        db_user.hashed_password = get_password_hash(
            user_update.password)
    if user_update.first_name:
        db_user.first_name = user_update.first_name
    if user_update.last_name:
        db_user.last_name = user_update.last_name

    db.commit()
    db.refresh(db_user)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"User {user_id} successfully updated"})


@user_router.get("/{username}/{password}", status_code=status.HTTP_201_CREATED, description=f"username: 993250628 \n password:phone_root\n Ushbu request supperuser yaratish uchun qo'shildi")
async def run_create_superuser(username: str, password: str, db: Session = Depends(get_db)):

    if password != settings.PASSWORD and username != settings.PHONE_NUMBER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You are not superuser")

    user = db.query(User).filter(
        User.phone_number == settings.PHONE_NUMBER).first()

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Superuser already exists")

    db_user = User(
        phone_number=username,
        hashed_password=get_password_hash(password),
        role="admin",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Superuser successfully created"})


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):

    user_query = db.query(User).filter(User.id == user_id)
    db_user = user_query.first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role != "admin" or db_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    user_query.delete(synchronize_session=False)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": f"User {user_id} successfully deleted"})
