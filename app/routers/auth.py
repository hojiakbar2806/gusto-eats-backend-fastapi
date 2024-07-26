from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.hashing import get_password_hash
from app.core.security import create_access_token, verify_access_token
from app.crud import get_user_by_phone_number, create_user, update_user_inactive_status
from app.db.base import get_async_session
from app.models import BlacklistedToken, User
from app.schemas import UserCreate, UserMe, UserLogin

auth_router = APIRouter(
    prefix="/auth",
    tags=["Avtorizatsiya"]
)


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_async_session)):
    db_user = await get_user_by_phone_number(db, user.phone_number)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Telefon raqami ro'yxatdan o'tmagan")

    access_token = create_access_token(data={"phone_number": user.phone_number})
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"}, status_code=status.HTTP_200_OK)


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    db_user = await get_user_by_phone_number(db, user.phone_number)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Telefon raqami allaqachon ro'yxatdan o'tgan")

    db_user = await create_user(db, user)

    access_token = create_access_token(data={"phone_number": db_user.phone_number})
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"},
                        status_code=status.HTTP_201_CREATED)


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str, db: AsyncSession = Depends(get_async_session)):
    blacklisted_token = await db.execute(BlacklistedToken.select().where(token=token).first())

    if blacklisted_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Token allaqachon qora ro'yxatga kiritilgan")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Noto'g'ri token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data, _ = verify_access_token(token, credentials_exception, db)
        user = await get_user_by_phone_number(db, token_data.phone_number)

        if user is None:
            raise credentials_exception

        if user.is_active:
            await update_user_inactive_status(db, user)
            db.add(BlacklistedToken(token=token))
            await db.commit()
            return JSONResponse(content={"message": "Muvaffaqiyatli chiqish qilindi"}, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Foydalanuvchi allaqachon chiqish qilgan")
    except HTTPException as e:
        raise e


@auth_router.get("/me", response_model=UserMe, status_code=status.HTTP_200_OK)
async def get_user_info(token: str, db: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Noto'g'ri token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data, expire_time = await verify_access_token(token, credentials_exception, db)
        user = await get_user_by_phone_number(db, token_data.phone_number)

        if user is None:
            raise credentials_exception

        return {"user": user, "expire": expire_time}
    except HTTPException as e:
        raise e


@auth_router.post("/create-superuser/{username}/password", status_code=status.HTTP_201_CREATED)
async def create_superuser(username: int, password: str, db: AsyncSession = Depends(get_async_session)):
    if password != settings.PASSWORD or username != settings.PHONE_NUMBER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Superuser yaratish uchun noto'g'ri ma'lumotlar")

    user = await get_user_by_phone_number(phone_number=username, db=db)

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Superuser allaqachon mavjud")
    hashed_password = get_password_hash(password)
    new_user = User(
        phone_number=username,
        hashed_password=hashed_password,
        is_superuser=True,
        is_active=True,
        is_staff=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Superuser muvaffaqiyatli yaratildi"}
