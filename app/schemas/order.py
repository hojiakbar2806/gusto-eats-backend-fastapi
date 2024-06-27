from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas import ProductResponse


class OrderItemCreateSchema(BaseModel):
    product_id: int
    quantity: int


class OrderCreateSchema(BaseModel):
    items: List[OrderItemCreateSchema]


class OrderItemSchema(BaseModel):
    quantity: int
    product: ProductResponse

    class Config:
        orm_mode = True


class OrderResponseSchema(BaseModel):
    id: int
    status: str
    total_price: float
    items: List[OrderItemSchema]
    created_at: datetime

    class Config:
        orm_mode = True


class OrdersResponseSchema(BaseModel):
    total_price:float
    orders: List[OrderResponseSchema]
