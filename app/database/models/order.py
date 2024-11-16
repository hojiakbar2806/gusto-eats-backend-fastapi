import enum

from sqlalchemy import Column, Integer, ForeignKey, Float, Enum, DateTime, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')


class OrderStatus(enum.Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
