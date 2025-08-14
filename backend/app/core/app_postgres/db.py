import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from backend.app import crud
from backend.app.config import settings
from backend.app.models import User, UserCreate

engine = create_async_engine(str(settings.APP_DATABASE_URI), echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.email == settings.FIRST_SUPERUSER)
            )
            user = result.scalars().first()

            if not user:
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                )
                await crud.create_user(session=session, user_create=user_in)