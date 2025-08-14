import pytest

from backend.app.services.api_services.user_service import UserService
from app.api.schemas.user_dto import UserCreate


@pytest.mark.asyncio
async def test_create_user(test_uow_cls):
    service = UserService(uow_cls=test_uow_cls)
    user = await service.create_user(UserCreate(name="Test", email="test@example.com"))
    assert user.email == "test@example.com"


