from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

engine = create_async_engine(
    url=settings.APP_DATABASE_URI,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


