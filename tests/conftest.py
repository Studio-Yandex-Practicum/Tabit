import uuid
from collections.abc import AsyncGenerator
from datetime import timedelta
from typing import Any

import pytest
import pytest_asyncio
from fastapi_users.password import PasswordHelper
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.companies.models import Company
from src.database import Base
from src.database.db_depends import get_async_session
from src.main import app_v1
from src.tabit_management.models import LicenseType, TabitAdminUser
from src.users.models import UserTabit
from src.users.models.enum import RoleUserTabit
from tests.constants import GOOD_PASSWORD, URL


@pytest.fixture
def test_db(postgresql):
    """Использование pytest-postgresql для тестовой БД."""
    database_url = (
        f'postgresql+psycopg://{postgresql.info.user}:{postgresql.info.password}@'
        f'{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}'
    )

    engine = create_async_engine(database_url, echo=False, poolclass=NullPool)
    TestingSessionLocal = async_sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False, autocommit=False
    )

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    pytest.db_engine = engine
    pytest.db_sessionmaker = TestingSessionLocal

    return init_db


@pytest_asyncio.fixture
async def async_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для сессии БД."""
    init_db = test_db
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


async def make_entry_in_table(async_session: AsyncSession, payload: dict[str, Any], model):
    """Функция создаст запись в указанной таблице согласно переданным данным."""
    new_entry = model(**payload)
    async_session.add(new_entry)
    await async_session.commit()
    await async_session.refresh(new_entry)
    return new_entry


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

        return await make_entry_in_table(async_session, default_data, LicenseType)

    return _create_license


@pytest_asyncio.fixture
async def company_1(async_session):
    """Фикстура для создания компании №1 в таблице company."""
    company_data = {
        'name': 'Zorg',
        'is_active': True,
        'slug': 'Zorg',
    }
    return await make_entry_in_table(async_session, company_data, Company)


@pytest_asyncio.fixture
async def superuser(async_session):
    """
    Фикстура для создания суперпользователя сервиса в таблице tabitadminuser.
    """

    superuser_data = {
        'name': 'Ип',
        'surname': 'Ман',
        'email': 'yandex@yandex.ru',
        'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
        'is_active': True,
        'is_superuser': True,
        'is_verified': False,
    }

    return await make_entry_in_table(async_session, superuser_data, TabitAdminUser)


@pytest_asyncio.fixture
async def admin(async_session: AsyncSession):
    """
    Фикстура для создания администратора сервиса в таблице tabitadminuser.
    """

    admin_data = {
        'name': 'Брюс',
        'surname': 'Ли',
        'email': 'mail@yandex.ru',
        'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
        'is_active': True,
        'is_superuser': False,
        'is_verified': False,
    }

    return await make_entry_in_table(async_session, admin_data, TabitAdminUser)


@pytest_asyncio.fixture
async def moderator_1_company_1(async_session: AsyncSession, company_1):
    """
    Фикстура для создания модератора от компании в таблице tabitadminuser.
    """

    moderator_data = {
        'name': 'Корбен ',
        'surname': 'Даллас',
        'email': 'yandex@yandex.ru',
        'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
        'is_active': True,
        'is_superuser': False,
        'is_verified': False,
        'role': RoleUserTabit.ADMIN,
        'company_id': company_1.id,
    }

    return await make_entry_in_table(async_session, moderator_data, UserTabit)


@pytest_asyncio.fixture
async def user_1_company_1(async_session: AsyncSession, company_1):
    """
    Фикстура для создания пользователя от компании в таблице tabitadminuser.
    """

    user = {
        'name': 'Руби ',
        'surname': 'Род',
        'email': 'mail@yandex.ru',
        'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
        'is_active': True,
        'is_superuser': False,
        'is_verified': False,
        'role': RoleUserTabit.EMPLOYEE,
        'company_id': company_1.id,
    }

    return await make_entry_in_table(async_session, user, UserTabit)


async def get_token(client: AsyncClient, user, url: str, refresh: bool = False) -> dict[str, str]:
    """Функция для получения тела заголовка с Authorization переданного пользователя."""

    login_payload = {'username': user.email, 'password': GOOD_PASSWORD}
    response = await client.post(url, data=login_payload)
    data = response.json()
    token = data['refresh_token'] if refresh else data['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
async def superuser_token(client: AsyncClient, superuser):
    """
    Фикстура для получения заголовков авторизации суперпользователя сервиса Tabit c access-token.
    """
    return await get_token(client, superuser, URL.ADMIN_LOGIN)


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, admin):
    """
    Фикстура для получения заголовков авторизации администратора сервиса Tabit c access-token.
    """
    return await get_token(client, admin, URL.ADMIN_LOGIN)


@pytest_asyncio.fixture
async def moderator_1_company_1_token(client: AsyncClient, moderator_1_company_1):
    """
    Фикстура для получения заголовков авторизации модератора от компании c access-token.
    """
    return await get_token(client, moderator_1_company_1, URL.USER_LOGIN)


@pytest_asyncio.fixture
async def user_1_company_1_token(client: AsyncClient, user_1_company_1):
    """
    Фикстура для получения заголовков авторизации пользователя от компании c access-token.
    """
    return await get_token(client, user_1_company_1, URL.USER_LOGIN)


@pytest_asyncio.fixture
async def superuser_refresh_token(client: AsyncClient, superuser):
    """
    Фикстура для получения заголовков авторизации суперпользователя сервиса Tabit c refresh-token.
    """
    return await get_token(client, superuser, URL.ADMIN_LOGIN, refresh=True)


@pytest_asyncio.fixture
async def admin_refresh_token(client: AsyncClient, admin):
    """
    Фикстура для получения заголовков авторизации администратора сервиса Tabit c refresh-token.
    """
    return await get_token(client, admin, URL.ADMIN_LOGIN, refresh=True)


@pytest_asyncio.fixture
async def moderator_company_refresh_token(client: AsyncClient, moderator_1_company_1):
    """
    Фикстура для получения заголовков авторизации модератора от компании c refresh-token.
    """
    return await get_token(client, moderator_1_company_1, URL.USER_LOGIN, refresh=True)


@pytest_asyncio.fixture
async def user_company_refresh_token(client: AsyncClient, user_1_company_1):
    """
    Фикстура для получения заголовков авторизации пользователя от компании c refresh-token.
    """
    return await get_token(client, user_1_company_1, URL.USER_LOGIN, refresh=True)
