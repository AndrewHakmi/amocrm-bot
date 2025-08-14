from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends

from app.api.schemas.catalog_dto import DeviceCreate, DeviceUpdate
from app.core.postgres.models.users import User

from app.core.security import get_password_hash, verify_password
from app.services.exceptions.catalog_err import DeviceAlreadyExistsError, DeviceNotFoundError
from app.services.exceptions.user_err import PhoneAlreadyExistsError, EmailAlreadyExistsError, UserNotFoundError
from app.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.services.uow.unit_of_work import AbstractUnitOfWork
from pydantic import BaseModel




class UserService:
    """UserService provides a high-level interface for handling user-related operations,
    including user registration, retrieval, and waitlist management.

    This class encapsulates business logic and interacts with the data access layer
    via the Unit of Work pattern to ensure atomic and consistent operations.

    Attributes:
        uow_cls (Type[AbstractUnitOfWork]): A class implementing the Unit of Work pattern,
            used to manage database transactions and access DAOs."""
    def __init__(self, uow_cls: type[AbstractUnitOfWork]):
        self.uow_cls = uow_cls


    async def get_all(self, skip, limit) -> list[BaseModel]:
        async with self.uow_cls() as uow:
            users = await uow.users.find_all(skip=skip, limit=limit)
            if not users:
                raise UserNotFoundError()
            return users

    async def authenticate(self, email: str, password: str):
        async with self.uow_cls() as uow:
            user = await uow.users.find_one_or_none({"email": email})
            if not user:
                return None
            if not verify_password(password, user.password):
                return None
            return user

    async def create_user(self, dto: BaseModel) -> User:
        async with self.uow_cls() as uow:
            if await uow.users.find_one_or_none({"email": dto.email}):
                raise EmailAlreadyExistsError()
            data = dto.model_dump()
            data["password"] = get_password_hash(dto.password)
            user = await uow.users.add(data)
            return user

    async def update_me(self, user_id: UUID, dto: BaseModel) -> User:
        async with self.uow_cls() as uow:
            if dto.email:
                existing = await uow.users.find_one_or_none({"email": dto.email})
                if existing and existing.id != user_id:
                    raise EmailAlreadyExistsError()
            user = await uow.users.find_one_or_none({"id": user_id})
            if not user:
                raise UserNotFoundError()
            await uow.users.update({"id": user.id, "email": user.email}, dto)
            return user



    async def delete_by_id(self, user_id: Optional[UUID]):
        async with self.uow_cls() as uow:
            existing = await uow.users.find_one_or_none({"id": user_id})
            if not existing:
                raise UserNotFoundError()
            await uow.users.delete({"id": user_id})


    async def find_by_id(self, user_id: Optional[UUID]) -> User:
        async with self.uow_cls() as uow:
            user = await uow.users.find_one_or_none({"id": user_id})
            if not user:
                raise UserNotFoundError()
            return user

    async def find_by_email(self, email: str) -> User | None:
        async with self.uow_cls() as uow:
            user = await uow.users.find_one_or_none({"email": email})
            if not user:
                return None
            return user

    async def list_devices(self, *, skip: int = 0, limit: int = 100):
        async with self.uow_cls() as uow:
            items = await uow.devices.find_all(skip=skip, limit=limit)
            return items or []

    async def create_device(self, dto: DeviceCreate):
        async with self.uow_cls() as uow:
            # проверка на дубликат (brand, type, name)
            existing = await uow.devices.find_one_or_none({
                "brand": dto.brand, "type": dto.type, "name": dto.name
            })
            if existing:
                raise DeviceAlreadyExistsError()
            created = await uow.devices.add(dto.model_dump())
            return created

    async def update_device(self, device_id: str, dto: DeviceUpdate):
        async with self.uow_cls() as uow:
            existing = await uow.devices.find_one_or_none({"id": device_id})
            if not existing:
                raise DeviceNotFoundError()
            # если меняем комбинацию, убедимся что не занята
            data = dto.model_dump(exclude_unset=True)
            if {"brand", "type", "name"}.issubset(data.keys()):
                dup = await uow.devices.find_one_or_none({
                    "brand": data["brand"], "type": data["type"], "name": data["name"]
                })
                if dup and str(dup.id) != str(device_id):
                    raise DeviceAlreadyExistsError()
            await uow.devices.update({"id": device_id}, data)
            return await uow.devices.find_one_or_none({"id": device_id})

    async def delete_device(self, device_id: str):
        async with self.uow_cls() as uow:
            existing = await uow.devices.find_one_or_none({"id": device_id})
            if not existing:
                raise DeviceNotFoundError()
            await uow.devices.delete({"id": device_id})






def get_user_service():
    return UserService(uow_cls=SQLAlchemyUnitOfWork)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]