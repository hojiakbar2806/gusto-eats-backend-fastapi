from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .settings import settings as env

SQLALCHEMY_DATABASE_URL = f"postgresql://{env.DB_USERNAME}:{
    env.DB_PASSWORD}@{env.DB_HOSTNAME}:{env.DB_PORT}/{env.DB_NAME}"




engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
