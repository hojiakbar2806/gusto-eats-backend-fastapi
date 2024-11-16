from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from app.database.models.user import Gender

from .mixin import Roles


class UserCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    chat_id: Optional[int] = None
    phone_number: int
    password: str
    gender: Gender


class UserResponse(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: int
    is_active: bool
    is_stuff: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    user: UserResponse
    expire: datetime


class UserListResponse(BaseModel):
    users: List[UserResponse]


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    phone_number: Optional[int]


class UserLogin(BaseModel):
    phone_number: int
    password: str
