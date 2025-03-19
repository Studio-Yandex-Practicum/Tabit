import subprocess
import time
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg2
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
from src.problems.models import CommentFeed, Meeting, MessageFeed, Problem
from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem
from src.tabit_management.models import LicenseType, TabitAdminUser
from src.users.models import UserTabit
from src.users.models.enum import RoleUserTabit
from tests.constants import GOOD_PASSWORD, TEST_DATABASE_URL, URL


def pytest_collection_modifyitems(items):
    """
    Добавляет всем тестам параметр loop_scope="session" в декоратор.
    Подробности: https://github.com/pytest-dev/pytest-asyncio/issues/922
    """
    pytest_asyncio_tests = (item for item in items if pytest_asyncio.is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope='session')
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    """
    Фикстура для автоматического запуска и удаления контейнера с тестовой базой данных.

    - Перед тестами запускает контейнер PostgreSQL с помощью `docker compose`.
    - Ожидает готовности базы перед выполнением тестов.
    - После тестов останавливает и удаляет контейнер с тестовой БД.

    Использует:
        - `docker compose -f infra/docker-compose.test-db.yaml up -d`
        - `docker compose -f infra/docker-compose.test-db.yaml down -v`
    """
    try:
        subprocess.run(
            ['docker', 'compose', '-f', 'infra/docker-compose.test-db.yaml', 'up', '-d'],
            check=True,
        )
        wait_for_postgres(
            host=TEST_DATABASE_URL.TEST_HOST,
            port=TEST_DATABASE_URL.TEST_PORT,
            user=TEST_DATABASE_URL.TEST_USER,
            password=TEST_DATABASE_URL.TEST_PASSWORD,
            dbname=TEST_DATABASE_URL.TEST_DBNAME,
        )
        yield
    finally:
        subprocess.run(
            ['docker', 'compose', '-f', 'infra/docker-compose.test-db.yaml', 'down', '-v'],
            check=True,
        )


def wait_for_postgres(host: str, port: int, user: str, password: str, dbname, timeout=30):
    """
    Ожидает готовности PostgreSQL перед началом тестов.

    - Проверяет соединение с БД в течение `timeout` секунд.
    - Если БД недоступна, делает повторные попытки подключения.
    - Если таймаут истёк, тесты не запустятся.

    Аргументы:
        host (str): Хост PostgreSQL.
        port (int): Порт PostgreSQL.
        user (str): Имя пользователя БД.
        password (str): Пароль пользователя БД.
        dbname (str, optional): Название тестовой БД. По умолчанию `test_db`.
        timeout (int, optional): Время ожидания, сек. По умолчанию 30 секунд.

    Исключения:
        TimeoutError: Если PostgreSQL не запустился за отведённое время.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = psycopg2.connect(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
            conn.close()
            print('✅ PostgreSQL готов к работе')
            return
        except psycopg2.OperationalError:
            print('⏳ Ожидание PostgreSQL...')
            time.sleep(1)
    raise TimeoutError('❌ PostgreSQL не запустился за отведённое время')


@pytest.fixture
def test_db():
    """
    Фикстура для настройки тестовой базы данных.

    - Использует переменные окружения из `.env` для конфигурации.
    - Создаёт асинхронный движок SQLAlchemy и сессию.
    - Обеспечивает создание и удаление всех таблиц перед и после тестов.
    - Гарантирует, что каждая тестовая сессия начинается с чистой базы данных.

    Возвращает:
        init_db (Callable): Функция для создания всех таблиц.
        drop_db (Callable): Функция для удаления всех таблиц.
    """

    database_url = (
        f'postgresql+asyncpg://{TEST_DATABASE_URL.TEST_USER}:{TEST_DATABASE_URL.TEST_PASSWORD}@'
        f'{TEST_DATABASE_URL.TEST_HOST}:{TEST_DATABASE_URL.TEST_PORT}/{TEST_DATABASE_URL.TEST_DBNAME}'
    )

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
    """
    Фикстура для создания асинхронной сессии БД перед каждым тестом.

    - Перед тестами сбрасывает БД, создавая чистое тестовое окружение.
    - Открывает новую сессию для тестов.
    - После теста автоматически выполняет `rollback()` и закрывает сессию.

    Возвращает:
        AsyncSession: Объект асинхронной сессии SQLAlchemy.
    """
    init_db, drop_db = test_db
    await drop_db()
    await init_db()

    session = pytest.db_sessionmaker()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def client(async_session):
    """
    Фикстура для создания тестового клиента FastAPI.

    - Подменяет зависимость `get_async_session`, чтобы тесты использовали тестовую БД.
    - Создаёт `AsyncClient` с `ASGITransport`, эмулируя HTTP-запросы.
    - Автоматически очищает `dependency_overrides` после завершения тестов.

    Возвращает:
        AsyncClient: Клиент для тестирования API.
    """

    async def override_get_async_session():
        async with async_session as session:
            try:
                yield session
            finally:
                await session.rollback()
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
    async with async_session as session:
        new_entry = model(**payload)
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry


@pytest_asyncio.fixture
async def license_for_test(async_session):
    """Фикстура, создающая тестовую лицензию с возможностью изменения полей."""

    async def _create_license(license_data=None):
        """Функция-обёртка для создания лицензии с изменяемыми параметрами."""
        default_data = {
            'name': f'Test License {uuid.uuid4().hex[:8]}',
            'license_term': timedelta(days=360),
            'max_admins_count': 5,
            'max_employees_count': 50,
        }

        if license_data:
            default_data.update(license_data)

        return await make_entry_in_table(async_session, default_data, LicenseType)

    return _create_license


@pytest_asyncio.fixture
async def company_for_test(async_session, license_for_test):
    """
    Фикстура, создающая тестовую компанию с возможностью изменения полей.
    По умолчанию, только обязательные поля.
    """

    async def _create_company(company_data=None, all_fields=False):
        """Функция-обёртка для создания компании с изменяемыми параметрами."""
        if not company_data or 'license_id' not in company_data:
            license_instance = await license_for_test()

        default_data = {
            'name': f'Test Company {uuid.uuid4().hex[:8]}',
            'slug': slugify(f'Test Company {uuid.uuid4().hex[:8]}'),
            'is_active': True,
        }
        if all_fields:
            default_data.update(
                {
                    'description': 'Тестовое описание компании',
                    'logo': 'https://example.com/logo.png',
                    'license_id': license_instance.id,
                    'start_license_time': datetime.now(timezone.utc).isoformat(),
                }
            )
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
        if not user_data or 'company_id' not in user_data:
            company = await company_for_test()
            company_id = company.id
        else:
            company_id = user_data.pop('company_id')
        default_data = {
            'name': 'Брюс',
            'surname': 'Ли',
            'email': f'{uuid.uuid4().hex[:8]}@yandex.ru',
            'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
            'is_active': True,
            'is_superuser': False,
            'is_verified': False,
            'role': RoleUserTabit.EMPLOYEE,
            'company_id': company_id,
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

 
# Фикстуры для тестов problem_feeds.py
@pytest_asyncio.fixture
async def problem_for_test(async_session: AsyncSession):
    """Фикстура, создающая проблему, связанную с переданным сотрудником и компанией"""

    async def _create_problem(employee, company_slug, problem_data=None):
        problem_obj = {
            'name': 'проблема',
            'description': 'описание проблемы',
            'color': ColorProblem.RED,
            'type': TypeProblem.B,
            'status': StatusProblem.NEW,
            'owner_id': employee.id,
            'company_slug': company_slug,
        }
        if problem_data:
            problem_obj.update(problem_data)
        return await make_entry_in_table(async_session, problem_obj, Problem)

    return _create_problem


@pytest_asyncio.fixture
async def message_feed_for_test(async_session: AsyncSession, problem_for_test):
    """Фикстура, создающая тред, принадлежащий переданному сотруднику"""

    async def _create_message_feed(
        employee, company_slug, message_feed_data=None, problem_id=None
    ):
        if not problem_id:
            problem = await problem_for_test(employee, company_slug)
            problem_id = problem.id
        message_feed_obj = {
            'problem_id': problem_id,
            'owner_id': employee.id,
            'text': 'текст треда',
            'important': True,
        }
        if message_feed_data:
            message_feed_obj.update(message_feed_data)
        return await make_entry_in_table(async_session, message_feed_obj, MessageFeed)

    return _create_message_feed


@pytest_asyncio.fixture
async def comment_for_test(async_session: AsyncSession, message_feed_for_test):
    """Фикстура, создающая комментарий, принадлежащий переданному сотруднику"""

    async def _create_comment(employee, company_slug, comment_data=None, message_feed_id=None):
        if not message_feed_id:
            message_feed = await message_feed_for_test(employee, company_slug)
            message_feed_id = message_feed.id
        comment_obj = {
            'text': 'текст комментария',
            'message_id': message_feed_id,
            'owner_id': employee.id,
        }
        if comment_data:
            comment_obj.update(comment_data)
        return await make_entry_in_table(async_session, comment_obj, CommentFeed)

    return _create_comment


@pytest_asyncio.fixture
async def problem_for_meeting(async_session: AsyncSession, employee_of_company, company_for_test):
    """Фикстура для создания проблемы."""

    async def func(company_slug=None, owner_id=None):
        if company_slug is None:
            company = await company_for_test()
            company_slug = company.slug
        if owner_id is None:
            owner = await employee_of_company()
            owner_id = owner.id
        default_data = {
            'name': 'Test Problem',
            'description': 'Some description',
            'company_slug': company_slug,
            'color': 1,
            'type': 'A',
            'status': 'Новая',
            'owner_id': owner_id,
        }
        problem = await make_entry_in_table(async_session, default_data, Problem)
        return problem

    return func


@pytest_asyncio.fixture
async def create_meeting(async_session: AsyncSession):
    """Фикстура для создания встречи."""

    async def func(problem_id, owner_id, count=1):
        meeting_data = {
            'title': f'Test Meeting {count}',
            'date_meeting': (datetime.now() + timedelta(days=count)).date(),
            'status': 'Новая',
            'problem_id': problem_id,
            'owner_id': str(owner_id),
        }
        meeting = await make_entry_in_table(async_session, meeting_data, Meeting)
        return meeting

    return func
