import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean, BigInteger, Enum, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class Gender(enum.Enum):
    MALE = "erkak"
    FEMALE = "ayol"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(BigInteger, unique=True, index=True)
    gender = Column(Enum(Gender, name='gender'), nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_stuff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reviews = relationship("Review", cascade="all, delete-orphan", back_populates="user")
    orders = relationship("Order", cascade="all, delete-orphan", back_populates="user")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
