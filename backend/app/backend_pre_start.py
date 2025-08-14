import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.postgres.db_engine import async_session_factory, engine


async def init(db_engine: AsyncEngine):
    try:
        async with async_session_factory() as session:
            await session.execute(select(1))
    except Exception as e:
        print("Database connection failed", exc_info=e)
        raise


async def main() -> None:
    await init(engine)



if __name__ == "__main__":
    asyncio.run(main())