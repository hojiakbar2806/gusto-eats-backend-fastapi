from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .review import ReviewResponse
from .category import CategoryResponse


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
    created_at: datetime
    category: Optional[CategoryResponse]
    reviews: List[ReviewResponse]
    average_rating: int

    class Config:
        from_attributes: True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
