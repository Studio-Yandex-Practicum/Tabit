import uuid
from collections.abc import AsyncGenerator
from datetime import timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.alembic_models import Base
from src.database.db_depends import get_async_session
from src.main import app_v1
from src.tabit_management.models import LicenseType


@pytest.fixture
def test_db(postgresql):
    """Использование pytest-postgresql для тестовой БД."""
    database_url = f'postgresql+psycopg://{postgresql.info.user}:{postgresql.info.password}@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}'

    engine = create_async_engine(database_url, echo=False, poolclass=NullPool)
    TestingSessionLocal = async_sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False, autocommit=False
    )

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    pytest.db_engine = engine
    pytest.db_sessionmaker = TestingSessionLocal

    return init_db, drop_db


@pytest_asyncio.fixture
async def async_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для сессии БД."""
    init_db, _ = test_db
    await init_db()

    async with pytest.db_sessionmaker() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def client(async_session):
    """Фикстура для тестового клиента API через ASGITransport."""

    async def override_get_async_session():
        async with pytest.db_sessionmaker() as session:
            yield session
            await session.close()

    app_v1.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(transport=ASGITransport(app_v1), base_url='http://test') as ac:
        try:
            yield ac
        finally:
            await ac.aclose()
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
