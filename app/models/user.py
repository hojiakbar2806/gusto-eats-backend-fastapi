from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas import Roles


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(Enum(Roles), default="user")
    reviews = relationship("Review", back_populates="user")



class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=datetime.utcnow)
