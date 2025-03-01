import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
import pytest_asyncio
from fastapi_users.password import PasswordHelper
from httpx import ASGITransport, AsyncClient
from slugify import slugify
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.companies.models.models import Company
from src.database.db_depends import get_async_session
from src.database.models import BaseTabitModel as Base
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


@pytest_asyncio.fixture
async def test_admin_token(client: AsyncClient, superadmin_user):
    """
    Фикстура для получения заголовков авторизации администратора.
    """
    login_payload = {'username': superadmin_user.email, 'password': 'password123'}

    response = await client.post('/api/v1/admin/auth/login', data=login_payload)
    assert response.status_code == 200, f'Ошибка авторизации: {response.text}'

    tokens = response.json()
    access_token = tokens['access_token']
    return {'Authorization': f'Bearer {access_token}'}


async def make_entry_in_table(async_session: AsyncSession, payload: dict[str, Any], model):
    """Функция создаст запись в указанной таблице согласно переданным данным."""
    new_entry = model(**payload)
    async_session.add(new_entry)
    await async_session.commit()
    await async_session.refresh(new_entry)
    return new_entry


@pytest_asyncio.fixture
async def license_for_test(async_session):
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
async def company_for_test(async_session):
    """
    Фикстура, создающая тестовую компанию с возможностью изменения полей.
    По умолчанию, только обязательные поля.
    """

    async def _create_company(company_data=None):
        """Функция-обёртка для создания компании с изменяемыми параметрами."""
        default_data = {
            'name': f'Test Company {uuid.uuid4().hex[:8]}',
            'slug': f'Test_Company_{uuid.uuid4().hex[:8]}',
            'is_active': True,
        }
        if company_data:
            default_data.update(company_data)
        return await make_entry_in_table(async_session, default_data, Company)

    return _create_company


@pytest_asyncio.fixture
async def administrator_tabit(async_session):

    async def _create_administrator_tabit(administrator_data=False):

        default_data = {
            'name': 'Ип',
            'surname': 'Ман',
            'email': f'{uuid.uuid4().hex[:8]}@yandex.ru',
            'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
            'is_active': True,
            'is_superuser': False,
            'is_verified': False,
        }
        if administrator_data:
            default_data.update(administrator_data)
        return await make_entry_in_table(async_session, default_data, TabitAdminUser)

    return _create_administrator_tabit


@pytest_asyncio.fixture
async def superuser(administrator_tabit):
    """
    Фикстура для создания суперпользователя сервиса в таблице tabitadminuser.
    """
    return await administrator_tabit({'is_superuser': True})


@pytest_asyncio.fixture
async def admin(administrator_tabit):
    """
    Фикстура для создания администратора сервиса в таблице tabitadminuser.
    """
    return await administrator_tabit()


@pytest_asyncio.fixture
async def employee_of_company(async_session: AsyncSession, company_for_test):
    """
    Фикстура, создающая пользователя тестовой компании с возможностью изменения полей.
    По умолчанию, только обязательные поля.
    """

    async def _create_employee(user_data=None):
        """Функция-обёртка для пользователя тестовой компании с изменяемыми параметрами."""
        company = await company_for_test()
        default_data = {
            'name': 'Брюс',
            'surname': 'Ли',
            'email': f'{uuid.uuid4().hex[:8]}@yandex.ru',
            'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
            'is_active': True,
            'is_superuser': False,
            'is_verified': False,
            'role': RoleUserTabit.EMPLOYEE,
            'company_id': company.id,
        }
        if user_data:
            default_data.update(user_data)
        return await make_entry_in_table(async_session, default_data, UserTabit)

    return _create_employee


@pytest_asyncio.fixture
async def moderator_of_company(employee_of_company):
    """
    Фикстура, создающая модератора тестовой компании с возможностью изменения полей.
    По умолчанию, только обязательные поля.
    """

    async def _create_moderator(moderator_data=None):
        """Функция-обёртка для модератора тестовой компании с изменяемыми параметрами."""
        default = moderator_data or {}
        default['role'] = RoleUserTabit.ADMIN
        return await employee_of_company(default)

    return _create_moderator


@pytest_asyncio.fixture
async def moderator(moderator_of_company):
    """
    Фикстура для создания модератора от компании в таблице tabitadminuser.
    """
    return await moderator_of_company()


@pytest_asyncio.fixture
async def employee(employee_of_company):
    """
    Фикстура для создания пользователя от компании в таблице tabitadminuser.
    """
    return await employee_of_company()


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
async def get_token_for_user(client: AsyncClient):
    """
    Фикстура, создающая заголовков авторизации пользователя от тестовой компании.

    Например, в тесте:
    ```
    class TestExample:

        @pytest.mark.asyncio
        async def test_example(self, employee_of_company):
            user_1 = await employee_of_company({name: user_1})
            user_2 = await employee_of_company({name: user_2})
            access_token_user_1 = await get_token_for_user(user_1)
            access_token_user_2 = await get_token_for_user(user_2)
            refresh_token_user_2 = await get_token_for_user(user_2, refresh=True)
    ```
    """

    async def _get_token_for_user(user, refresh: bool = False):
        """Функция-обёртка для заголовков авторизации пользователя от тестовой компании."""
        return await get_token(client, user, URL.USER_LOGIN, refresh)

    return _get_token_for_user


@pytest_asyncio.fixture
async def moderator_token(get_token_for_user, moderator):
    """
    Фикстура для получения заголовков авторизации модератора от компании c access-token.
    """
    return await get_token_for_user(moderator)


@pytest_asyncio.fixture
async def employee_token(get_token_for_user, employee):
    """
    Фикстура для получения заголовков авторизации пользователя от компании c access-token.
    """
    return await get_token_for_user(employee)


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
async def moderator_refresh_token(get_token_for_user, moderator):
    """
    Фикстура для получения заголовков авторизации пользователя от компании c refresh-token.
    """
    return await get_token_for_user(moderator, refresh=True)


@pytest_asyncio.fixture
async def employee_refresh_token(get_token_for_user, employee):
    """
    Фикстура для получения заголовков авторизации пользователя от компании c refresh-token.
    """
    return await get_token_for_user(employee, refresh=True)
