from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .settings import settings

# SQLALCHEMY_DATABASE_URL = f"postgresql://:{settings.DB_USERNAME}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"
SQLALCHEMY_DATABASE_URL = f"postgresql://:root@db:5432/fastapi"


Base = declarative_base()

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
