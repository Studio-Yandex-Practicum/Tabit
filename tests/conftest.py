import uuid
from collections.abc import AsyncGenerator
from datetime import timedelta

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import Base
from src.database.db_depends import get_async_session
from src.main import app_v1
from src.tabit_management.models import LicenseType

TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_database():
    """Создание тестовой базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для сессии БД"""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(async_session):
    """Фикстура для тестового клиента API через ASGITransport"""

    def override_get_async_session():
        yield async_session

    app_v1.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(transport=ASGITransport(app_v1), base_url='http://test') as ac:
        try:
            yield ac
        finally:
            app_v1.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_license(async_session):
    """Фикстура, создающая тестовую лицензию с возможностью изменения полей."""

    async def _create_license(license_data=None):
        """Функция-обёртка для создания лицензии с изменяемыми параметрами."""
        default_data = {
            'name': f'Test License {uuid.uuid4().hex[:8]}',
            'license_term': timedelta(days=1),
            'max_admins_count': 5,
            'max_employees_count': 50,
        }

        if license_data:
            default_data.update(license_data)

        new_license = LicenseType(**default_data)
        async_session.add(new_license)
        await async_session.commit()
        await async_session.refresh(new_license)

        return new_license

    return _create_license
