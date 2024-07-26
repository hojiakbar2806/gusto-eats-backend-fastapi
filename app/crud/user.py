from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import update

from app.core.hashing import get_password_hash
from app.db.base import get_async_session
from app.models import User
from app.schemas import UserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_chat_id(session: AsyncSession, chat_id: int) -> Optional[User]:
    stmt = select(User).filter(User.chat_id == chat_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_admins_chat_id(session: AsyncSession) -> Sequence[int]:
    stmt = select(User.chat_id).filter(User.is_admin == True)
    result = await session.execute(stmt)
    return [row[0] for row in result]


async def promote_to_admin(chat_id: int) -> bool:
    async with get_async_session() as session:
        stmt = update(User).where(User.chat_id == chat_id).values(is_admin=True)
        await session.execute(stmt)
        await session.commit()
        return True


async def update_user_active_status(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_inactive_status(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_phone_number(db: AsyncSession, phone_number: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        gender=user.gender,
        hashed_password=hashed_password,
        chat_id=user.chat_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()

    if db_user:
        if user_update.phone_number:
            db_user.phone_number = user_update.phone_number
        if user_update.password:
            db_user.hashed_password = get_password_hash(user_update.password)
        if user_update.first_name:
            db_user.first_name = user_update.first_name
        if user_update.last_name:
            db_user.last_name = user_update.last_name
        await db.commit()
        await db.refresh(db_user)
        return db_user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")


async def delete_user(db: AsyncSession, user_id: int) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()

    if db_user:
        db_user.is_active = False
        await db.commit()
        return {"message": f"Foydalanuvchi {user_id} muvaffaqiyatli o'chirildi"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")
