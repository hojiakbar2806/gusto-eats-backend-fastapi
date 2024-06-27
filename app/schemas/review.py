
from typing import List
from pydantic import BaseModel
from datetime import datetime
from .user import UserResponse


class ReviewCreate(BaseModel):
    rating: int
    product_id:int
    name: str
    comment: str



class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str
    name: str
    # user: UserResponse
    # user_id: int
    # product_id: int
    created_at: datetime

    class Config:
        from_attributes = True
