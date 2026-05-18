import asyncio
import os
import sys

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.database import get_db
from app.db.base import Base
from app.main import app
from app.models import models
from app.models import user


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@127.0.0.1:55433/app_test_db",
)

if TEST_DATABASE_URL.startswith("postgresql+asyncpg://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql+psycopg://",
        1,
    )

TEST_DATABASE_URL = TEST_DATABASE_URL.replace("@localhost:", "@127.0.0.1:")
TEST_DATABASE_URL = TEST_DATABASE_URL.replace(":5433/app_test_db", ":55433/app_test_db")

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_test_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture
def user_payload():
    return {
        "username": "andrii",
        "email": "andrii@example.com",
        "password": "strong-password",
    }
