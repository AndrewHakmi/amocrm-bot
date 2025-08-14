from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgres.base import BaseDAO
from app.core.postgres.dao import UserDAO
from app.core.postgres.db_engine import async_session_factory
from app.services.uow.unit_of_work import AbstractUnitOfWork


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session = async_session_factory()
        self.users: BaseDAO = UserDAO(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()