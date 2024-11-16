import logging
from contextlib import asynccontextmanager

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=20,         # Ulanishlar poolining o'lchami
    max_overflow=10,      # Qo'shimcha ulanishlar
    pool_timeout=30       # Ulanish uchun kutish vaqti
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    async_session_instance = async_session_maker()
    try:
        yield async_session_instance
    finally:
        await async_session_instance.close()


async def create_tables():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logging.info("Database schema created successfully.")
    except ProgrammingError as e:
        if "duplicate table" in str(e):
            logging.warning("Jadval allaqachon mavjud, e'tiborsiz qoldirilmoqda.")
        else:
            logging.error(f"Error creating tables: {e}")
            raise e
