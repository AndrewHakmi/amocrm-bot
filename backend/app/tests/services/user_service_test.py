import pytest

from backend.app.domain.services.api_services.user_service import UserService
from backend.app.domain.services.schemas.user_dto import CreateUser


@pytest.mark.asyncio
async def test_create_user(test_uow_cls):
    service = UserService(uow_cls=test_uow_cls)
    user = await service.create_user(CreateUser(name="Test", email="test@example.com"))
    assert user.email == "test@example.com"


