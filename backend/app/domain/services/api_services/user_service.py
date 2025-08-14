from typing import Annotated
from fastapi import Depends
from backend.app.core.app_postgres.dao import UserDAO
from backend.app.models import User
from backend.app.domain.services.schemas.user_dto import CreateUser
from backend.app.domain.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from backend.app.domain.services.uow.unit_of_work import AbstractUnitOfWork


class UserService:
    def __init__(self, uow_cls: type[AbstractUnitOfWork]):
        self.uow_cls = uow_cls

    async def create_user(self, dto: CreateUser) -> User:
        async with self.uow_cls() as uow:
            users = UserDAO(uow.session)
            existing = await users.find_one_or_none({"email": dto.email})
            if existing:
                raise ValueError("User already exists")
            return await users.add(User(**dto.model_dump()))


def get_user_service() -> UserService:
    return UserService(uow_cls=SQLAlchemyUnitOfWork)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]