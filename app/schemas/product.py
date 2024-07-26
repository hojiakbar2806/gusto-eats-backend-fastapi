from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .category import CategoryResponse
from .review import ReviewResponse


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    type: str
    price: int
    image: str
    discount: int
    count_in_stock: int
    total_review: int
    average_rating: int
    created_at: datetime
    category: CategoryResponse  # Update: category should be singular
    reviews: List[ReviewResponse]

    class Config:
        from_attributes: True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
