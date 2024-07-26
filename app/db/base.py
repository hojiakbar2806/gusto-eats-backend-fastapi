from contextlib import asynccontextmanager

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


async def get_async_session() -> AsyncSession:
    async_session_instance = async_session_maker()
    try:
        yield async_session_instance
    finally:
        await async_session_instance.close()

@asynccontextmanager
async def get_session():
    async_session = async_session_maker()
    try:
        yield async_session
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e
    finally:
        await async_session.close()