
from typing import List
from pydantic import BaseModel
from datetime import datetime


class CategoryResponse(BaseModel):
    id: int
    name: str
    image_path: str

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]

    class Config:
        from_attributes = True
