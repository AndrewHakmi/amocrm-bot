import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from backend.app.config import settings
from backend.app.core.app_postgres.db_engine import Base
from backend.app.main import app
from backend.app.tests.utils.user import authentication_token_from_email
from backend.app.tests.utils.utils import get_superuser_token_headers

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)


# Asynchronous event loop for the entire scope
@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


# Database initialization
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Session for DAO, services, fixtures
@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


# Test client
@pytest.fixture(scope="function")
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Superuser's token
@pytest.fixture(scope="function")
async def superuser_token_headers(async_client: AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    return await get_superuser_token_headers(async_client, db_session)


# Regular user's token
@pytest.fixture(scope="function")
async def normal_user_token_headers(async_client: AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    return await authentication_token_from_email(
        client=async_client,
        email=settings.EMAIL_TEST_USER,
        db=db_session
    )