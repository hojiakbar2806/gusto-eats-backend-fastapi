from typing import Type

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import bot
from app.core.config import settings
from app.database.models import Order, OrderItem, Product
from app.schemas import OrderCreateSchema, UserResponse


async def send_telegram_message(message: str):
    try:
        await bot.send_message(chat_id=settings.OWNER_ID, text=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram xabarini jo'natishda xato: {str(e)}")


async def create_order(db: AsyncSession, order_data: OrderCreateSchema, current_user: UserResponse) -> Order:
    try:
        total_price = 0
        order_items = []

        async with db.begin() as transaction:
            for item in order_data.items:
                product = await db.get(Product, item.product_id)
                if not product:
                    raise HTTPException(status_code=404, detail=f"Mahsulot {item.product_id} topilmadi")

                if product.count_in_stock < item.quantity:
                    raise HTTPException(status_code=400,
                                        detail=f"Mahsulot {item.product_id} uchun yetarli miqdor yo'q")

                if item.quantity == 0:
                    raise HTTPException(status_code=400, detail="Mahsulot miqdori nolga teng bo'lishi mumkin emas")

                item_price = product.price * item.quantity
                total_price += item_price
                product.count_in_stock -= item.quantity

                order_item = OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item_price
                )
                db.add(order_item)
                order_items.append(order_item)

            order = Order(user_id=current_user.id, status="kutmoqda", total_price=total_price)
            db.add(order)
            await db.flush()

            for order_item in order_items:
                order_item.order_id = order.id

        await db.commit()
        await db.refresh(order)

        return order

    except SQLAlchemyError as e:
        await db.rollback()
        error_message = f"Buyurtmani yaratishda xato: {str(e)}"
        await send_telegram_message(error_message)
        raise HTTPException(status_code=500, detail=error_message)


async def get_orders(db: AsyncSession, current_user: UserResponse):
    try:
        orders_query = await db.execute(select(Order).where(Order.user_id == current_user.id))
        orders = orders_query.scalars().all()

        if not orders:
            raise HTTPException(status_code=404, detail="Joriy foydalanuvchi uchun buyurtmalar topilmadi")

        total_price = sum(order.total_price for order in orders)
        return {"total_price": total_price, "orders": orders}

    except SQLAlchemyError as e:
        error_message = f"Buyurtmalarni olishda xato: {str(e)}"
        await send_telegram_message(error_message)
        raise HTTPException(status_code=500, detail=error_message)


async def update_order(db: AsyncSession, order_id: int, order_data: OrderCreateSchema) -> Type[Order]:
    try:
        order = await db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Buyurtma {order_id} topilmadi")

        order.status = order_data.status
        await db.commit()
        await db.refresh(order)

        return order

    except SQLAlchemyError as e:
        await db.rollback()
        error_message = f"Buyurtmani yangilashda xato: {str(e)}"
        await send_telegram_message(error_message)
        raise HTTPException(status_code=500, detail=error_message)


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    try:
        order = await db.get(Order, order_id)
        if not order:
            return False

        await db.delete(order)
        await db.commit()
        return True

    except SQLAlchemyError as e:
        await db.rollback()
        error_message = f"Buyurtmani o'chirishda xato: {str(e)}"
        await send_telegram_message(error_message)
        raise HTTPException(status_code=500, detail=error_message)
