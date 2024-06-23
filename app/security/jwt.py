from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.settings import settings
from app.models import User, BlacklistedToken
from app.schemas import TokenData
from app.database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException, db: Session):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        phone_number: str = payload.get("phone_number")
        if phone_number is None:
            raise credentials_exception

        blacklisted_token = db.query(
            BlacklistedToken).filter_by(token=token).first()
        if blacklisted_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has been invalidated", headers={"WWW-Authenticate": "Bearer"},)

        expire_time = datetime.utcfromtimestamp(payload.get("exp"))
        token_data = TokenData(phone_number=phone_number)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired", headers={"WWW-Authenticate": "Bearer"},)
    except JWTError:
        raise credentials_exception
    return token_data, expire_time


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},
                                          )
    blacklisted_token = db.query(
        BlacklistedToken).filter_by(token=token).first()
    if blacklisted_token is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token=token,  key=settings.SECRET_KEY, algorithms=[
                             settings.ALGORITHM])
        phone_number: int = payload.get("phone_number")
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(
        User.phone_number == phone_number).first()
    if user is None:
        raise credentials_exception
    return user
