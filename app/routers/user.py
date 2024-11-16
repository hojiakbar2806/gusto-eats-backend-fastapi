from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.crud import get_user_by_id, get_users, create_user, update_user, delete_user, get_user_by_phone_number
from app.database.base import get_async_session
from app.schemas import UserCreate, UserResponse, UserListResponse, UserUpdate

user_router = APIRouter(prefix="/users", tags=['Users'])


@user_router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, current_user: UserResponse = Depends(get_current_user),
                               db: AsyncSession = Depends(get_async_session)):
    if not current_user.is_stuff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    existing_user = await get_user_by_phone_number(db, user.phone_number)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Phone number already registered")

    created_user = await create_user(db, user)
    return created_user


@user_router.get("/", response_model=UserListResponse)
async def read_all_users_endpoint(skip: int = 0, limit: int = 100,
                                  current_user: UserResponse = Depends(
                                      get_current_user),
                                  db: AsyncSession = Depends(get_async_session)):
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    users = await get_users(db, skip, limit)
    return {"users": users}


@user_router.get('/{user_id}', response_model=UserResponse)
async def read_user_by_id_endpoint(user_id: int,
                                   current_user: UserResponse = Depends(
                                       get_current_user),
                                   db: AsyncSession = Depends(get_async_session)):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != db_user.id and not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    return db_user


@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user_update: UserUpdate,
                               current_user: UserResponse = Depends(
                                   get_current_user),
                               db: AsyncSession = Depends(get_async_session)):
    db_user = await get_user_by_id(db, user_id)
    if current_user.id != db_user.id and not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    return await update_user(db, user_id, user_update)


@user_router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int,
                               current_user: UserResponse = Depends(
                                   get_current_user),
                               db: AsyncSession = Depends(get_async_session)):
    db_user = await get_user_by_id(db, user_id)

    if current_user.id != db_user.id and not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    return await delete_user(db, user_id)
