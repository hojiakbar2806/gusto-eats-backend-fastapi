from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.crud.order import create_order, get_orders, update_order, delete_order
from app.db.base import get_async_session
from app.schemas import OrderCreateSchema, OrderResponseSchema, OrdersResponseSchema, UserResponse

order_router = APIRouter(tags=['Orders'], prefix="/orders")


@order_router.post("/create", response_model=OrderResponseSchema)
async def create_order_api(
        order_data: OrderCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserResponse = Depends(get_current_user)
):
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin user can't add order")

    return await create_order(db, order_data, current_user)


@order_router.get("/", response_model=OrdersResponseSchema)
async def read_orders_api(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserResponse = Depends(get_current_user)
):
    return await get_orders(db, current_user)


@order_router.put("/{order_id}", response_model=OrderResponseSchema)
async def update_order_api(
        order_id: int,
        order_data: OrderCreateSchema,
        db: AsyncSession = Depends(get_async_session)
):
    return await update_order(db, order_id, order_data)


@order_router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_api(
        order_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    success = await delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Buyurtma {order_id} topilmadi")
    return None
