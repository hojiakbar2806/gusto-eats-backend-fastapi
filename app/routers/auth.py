from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserMe, UserLogin
from app.models import User, BlacklistedToken
from app.database import get_db
from app.security import create_access_token, verify_access_token, get_password_hash

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authorization"]
)


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.phone_number == user.phone_number).first()
    if not db_user:
        raise HTTPException(
            status_code=400, detail="Phone number is not registered")

    if not db_user.is_active:
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)

    access_token = create_access_token(
        data={"phone_number": user.phone_number})

    return JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        status_code=status.HTTP_200_OK
    )


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Phone number already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = (create_access_token(
        data={"phone_number": db_user.phone_number}))
    return JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        status_code=status.HTTP_201_CREATED
    )


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str, db: Session = Depends(get_db)):
    blacklisted_token = db.query(
        BlacklistedToken).filter_by(token=token).first()

    if blacklisted_token is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token is already blacklisted"
        )

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data, expire_time = verify_access_token(
            token=token, credentials_exception=credentials_exception, db=db)
        user = db.query(User).filter(
            User.phone_number == token_data.phone_number).first()

        if user is None:
            raise credentials_exception

        if user.is_active:
            user.is_active = False
            db.add(BlacklistedToken(token=token))
            db.commit()
            return JSONResponse(
                content={"message": "Successfully logged out"},
                status_code=status.HTTP_201_CREATED
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is already logged out"
            )
    except HTTPException as e:
        raise e


@auth_router.get("/auth/me", response_model=UserMe, status_code=status.HTTP_200_OK)
async def get_user_info(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data, expire_time = verify_access_token(
            token=token, credentials_exception=credentials_exception, db=db)
        print(token_data)
        user = db.query(User).filter(User.phone_number ==
                                     token_data.phone_number).first()
        if user is None:
            raise credentials_exception

        return {"user": user, "expire": expire_time}
    except HTTPException as e:
        raise e
