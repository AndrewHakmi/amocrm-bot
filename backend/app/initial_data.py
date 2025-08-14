import asyncio

from app.api.schemas.enums.users import LmsRole
from app.config import settings

from app.core.app_logger import logger
from app.core.security import get_password_hash
from app.services.api_services.user_service import UserService
from app.api.schemas.user_dto import UserCreate
from app.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork

async def init_db() -> None:
    user_service = UserService(uow_cls=SQLAlchemyUnitOfWork)
    if not await user_service.find_by_email(settings.FIRST_SUPERUSER):
        super_user = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True
            )
        await user_service.create_user(super_user)




async def main() -> None:
    logger.info("Creating initial data")
    await init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
