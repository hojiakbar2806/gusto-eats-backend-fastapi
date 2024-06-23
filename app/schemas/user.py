from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from .mixin import Roles
from datetime import datetime


class UserCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: int
    password: str
    role: Roles = "user"


class UserResponse(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: int
    role: Roles = "user"
    is_active: bool

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
