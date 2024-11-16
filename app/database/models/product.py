from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import relationship

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    discount = Column(Float, nullable=False)
    count_in_stock = Column(Integer, nullable=False)
    total_review = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, default=0, nullable=False)
    image = Column(String, nullable=False)
    telegram_file_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey(
        "products.id", ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    image_path = Column(String, nullable=False)
    telegram_file_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    products = relationship("Product", back_populates="category")

