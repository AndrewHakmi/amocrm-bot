from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.postgres.db_engine import async_session_factory

class AbstractUnitOfWork(ABC):
    session: AsyncSession

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

    @abstractmethod
    async def close(self):
        ...