from datetime import datetime, timedelta

from jose import JWTError, jwt
from sqlalchemy.future import select
from jwt import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.schemas import TokenData
from app.core.config import settings
from app.database.base import get_async_session
from app.database.models import User, BlacklistedToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def verify_access_token(token: str, credentials_exception: HTTPException, db: AsyncSession):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        phone_number: str = payload.get("phone_number")
        if phone_number is None:
            raise credentials_exception

        blacklisted_token = await db.execute(select(BlacklistedToken).where(BlacklistedToken.token == token))
        if blacklisted_token.scalar():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has been invalidated", headers={"WWW-Authenticate": "Bearer"})

        expire_time = datetime.utcfromtimestamp(payload.get("exp"))
        token_data = TokenData(phone_number=phone_number)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired", headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise credentials_exception

    return token_data, expire_time


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    blacklisted_token = await db.execute(select(BlacklistedToken).where(BlacklistedToken.token == token))
    if blacklisted_token.scalar():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[
                             settings.ALGORITHM])
        phone_number: str = payload.get("phone_number")
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.execute(select(User).where(User.phone_number == phone_number))
    user = user.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user
