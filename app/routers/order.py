from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models import Order, OrderItem, Product
from app.schemas import OrderCreateSchema, OrderResponseSchema, UserResponse
from app.schemas.order import OrdersResponseSchema
from app.security import get_current_user

order_router = APIRouter(tags=['Orders'], prefix="/orders")


@order_router.post("/create", response_model=OrderResponseSchema)
async def create_order(
    order_data: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):

    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin user can't add order")
    try:
        total_price = 0
        order_items = []

        # Start a new transaction
        with db.begin_nested():
            for item in order_data.items:
                product = db.query(Product).filter(
                    Product.id == item.product_id).with_for_update().first()
                if not product:
                    raise HTTPException(
                        status_code=404, detail=f"Product not found with id {item.product_id}")

                if product.count_in_stock < item.quantity:
                    raise HTTPException(
                        status_code=400, detail=f"Not enough stock for product with id {item.product_id}")

                if item.quantity == 0:
                    raise HTTPException(
                        status_code=400, detail="Item quantity must be greater than zero")

                item_price = product.price * item.quantity
                total_price += item_price
                product.count_in_stock -= item.quantity

                order_item = OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item_price
                )
                order_items.append(order_item)

            # Create the order
            order = Order(user_id=current_user.id,
                          status="pending", total_price=total_price)
            db.add(order)
            db.flush()

            for order_item in order_items:
                order_item.order_id = order.id
                db.add(order_item)

        db.commit()
        db.refresh(order)

        return order

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@order_router.get("/", response_model=OrdersResponseSchema)
async def read_orders(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    try:
        if current_user.role == "admin":
            orders = db.query(Order).all()
            if not orders:
                raise HTTPException(
                    status_code=404, detail="No orders found for the current user")
            total_price = sum(order.total_price for order in orders)
            print(orders)
            return {"total_price": total_price, "orders": orders}

        orders = db.query(Order).filter(Order.user_id == current_user.id).all()
        if not orders:
            raise HTTPException(
                status_code=404, detail="No orders found for the current user")
        total_price = sum(order.total_price for order in orders)
        return {"total_price": total_price, "orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
