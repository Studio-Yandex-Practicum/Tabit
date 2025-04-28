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
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database.db_depends import get_async_session
from src.main import app_v1
from src.models import (
    AssociationUserComment,
    BaseTabitModel,
    CommentFeed,
    Company,
    CompanyUser,
    CompanyUserRole,
    Department,
    LicenseType,
    Meeting,
    MessageFeed,
    Problem,
    ProblemColor,
    ProblemStatus,
    ProblemType,
    TabitAdminUser,
)
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
            await conn.run_sync(BaseTabitModel.metadata.create_all)

    async def drop_db():
        async with engine.begin() as conn:
            await conn.run_sync(BaseTabitModel.metadata.drop_all)
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
    """
    Фикстура, создающая тестовую лицензию с возможностью изменения полей.

    Параметры:
        - license_data (dict, optional): Данные для создания лицензии. Если не переданы,
          используются значения по умолчанию.

    Возвращает:
        - LicenseType: Объект созданной лицензии.

    Примеры использования:
        # Создание лицензии с данными по умолчанию
        license_instance = await license_for_test()

        # Создание лицензии с кастомными параметрами
        license_instance = await license_for_test(
            {'name': 'Премиум Лицензия', 'max_admins_count': 10}
        )
    """

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

    Параметры:
        - company_data (dict, optional): Данные для создания компании. Если не переданы,
          используются значения по умолчанию.
        - all_fields (bool, optional): Если True, создаётся компания со всеми возможными полями.
        - return_license (bool, optional): Если True, возвращает объект лицензии
          вместе с компанией.
        - with_department (bool, optional): Если True, создаётся также департамент
          и возвращается вместе с компанией.

    Возвращает:
        - Company: Объект созданной компании.
        - (Company, LicenseType): Если `return_license=True`,
           возвращает кортеж (компания, лицензия).
        - (Company, Department): Если `with_department=True`,
           возвращает кортеж (компания, департамент).

    Примеры использования:
        # Создание компании только с обязательными полями
        company = await company_for_test()

        # Создание компании с кастомными данными
        company = await company_for_test({'name': 'Моя Компания', 'license_id': 123})

        # Создание компании со всеми полями
        company = await company_for_test(all_fields=True)

        # Получение компании и лицензии
        company, license_instance = await company_for_test(return_license=True)
    """

    async def _create_company(
        company_data=None, all_fields=False, return_license=False, with_department=False
    ):
        """Функция-обёртка для создания компании с изменяемыми параметрами."""
        license_instance = None

        if not company_data or 'license_id' not in company_data and all_fields:
            license_instance = await license_for_test()

        default_data = {
            'name': f'Test Company {uuid.uuid4().hex[:8]}',
            'slug': slugify(f'Test Company {uuid.uuid4().hex[:8]}'),
            'is_active': True,
        }
        if all_fields:
            license_id = (
                company_data.get('license_id')
                if company_data and 'license_id' in company_data
                else license_instance.id
            )

            default_data.update(
                {
                    'description': 'Тестовое описание компании',
                    'logo': 'https://example.com/logo.png',
                    'license_id': license_id,
                    'start_license_time': datetime.now(timezone.utc).isoformat(),
                }
            )
        if company_data:
            default_data.update(company_data)
        company = await make_entry_in_table(async_session, default_data, Company)

        department = None
        if with_department:
            department_data = {
                'name': f'Department {uuid.uuid4().hex[:8]}',
                'company_id': company.id,
                'slug': slugify(f'Department {uuid.uuid4().hex[:8]}'),
            }
            department = await make_entry_in_table(async_session, department_data, Department)

        if return_license:
            return company, license_instance
        if with_department:
            return company, department
        return company

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

    Параметры:
        - user_data (dict, optional): Данные для создания пользователя. Если не переданы,
          используются значения по умолчанию.
        - return_company (bool, optional): Если True, возвращает объект компании
          вместе с пользователем.

    Возвращает:
        - CompanyUser: Объект созданного пользователя.
        - (CompanyUser, Company): Если `return_company=True`, возвращает кортеж
          (пользователь, компания).

    Примеры использования:
        # Создание пользователя только с обязательными полями
        employee = await employee_of_company()

        # Создание пользователя с кастомными параметрами
        employee = await employee_of_company({'name': 'Джон', 'role': CompanyUserRole.MANAGER})

        # Получение пользователя и компании
        employee, company = await employee_of_company(return_company=True)
    """

    async def _create_employee(user_data=None, return_company=False):
        """Функция-обёртка для пользователя тестовой компании с изменяемыми параметрами."""
        company = None

        if not user_data or 'company_id' not in user_data:
            company = await company_for_test()

        company_id = (
            user_data.get('company_id') if user_data and 'company_id' in user_data else company.id
        )

        default_data = {
            'name': f'Брюс {uuid.uuid4().hex[:8]}',
            'surname': f'Ли {uuid.uuid4().hex[:8]}',
            'email': f'{uuid.uuid4().hex[:8]}@yandex.ru',
            'hashed_password': PasswordHelper().hash(GOOD_PASSWORD),
            'is_active': True,
            'is_superuser': False,
            'is_verified': False,
            'role': CompanyUserRole.EMPLOYEE,
            'company_id': company_id,
        }
        if user_data:
            default_data.update(user_data)
        employee = await make_entry_in_table(async_session, default_data, CompanyUser)

        if return_company:
            return employee, company
        return employee

    return _create_employee


@pytest_asyncio.fixture
async def moderator_of_company(employee_of_company):
    """
    Фикстура, создающая модератора тестовой компании с возможностью изменения полей.

    Параметры:
        - moderator_data (dict, optional): Данные для создания модератора. Если не переданы,
          используются значения по умолчанию.
        - return_company (bool, optional): Если True, возвращает объект компании
          вместе с модератором.

    Возвращает:
        - CompanyUser: Объект созданного модератора.
        - (CompanyUser, Company): Если `return_company=True`, возвращает кортеж
          (модератор, компания).

    Примеры использования:
        # Создание модератора только с обязательными полями
        moderator = await moderator_of_company()

        # Создание модератора с кастомными параметрами
        moderator = await moderator_of_company({
            'name': 'Иван',
            'email': 'ivan@example.com',
            'role': CompanyUserRole.MODERATOR
        })

        # Получение модератора и компании
        moderator, company = await moderator_of_company(return_company=True)
    """

    async def _create_moderator(moderator_data=None, return_company=False):
        """Функция-обёртка для модератора тестовой компании с изменяемыми параметрами."""
        default = moderator_data or {}
        default['role'] = CompanyUserRole.MODERATOR

        if return_company:
            return await employee_of_company(default, return_company=True)
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
        async def test_example(self, employee_of_company, get_token_for_user):
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


@pytest_asyncio.fixture
async def problem_for_test(async_session: AsyncSession, employee_of_company):
    """
    Фикстура, создающая проблему с возможностью изменения полей.

    Параметры:
        - problem_data (dict, optional): Данные для создания проблемы. Если не переданы,
          используются значения по умолчанию.
        - return_all_objects (bool, optional): Если True, возвращает кортеж
          (проблема, сотрудник, компания).

    Возвращает:
        - Problem: Объект созданной проблемы.
        - (Problem, CompanyUser, Company): Если `return_all_objects=True`,
           возвращает кортеж (проблема, сотрудник, компания).

    Примеры использования:
        # Создание проблемы только с обязательными полями
        problem = await problem_for_test()

        # Создание проблемы с кастомными параметрами
        problem = await problem_for_test({
            'name': 'Важная проблема',
            'color': ProblemColor.RED,
            'type': ProblemType.A
        })

        # Получение проблемы, сотрудника и компании
        problem, employee, company = await problem_for_test(return_all_objects=True)
    """

    async def _create_problem(problem_data=None, return_all_objects=False):
        """Функция-обёртка для создания проблемы с изменяемыми параметрами."""
        employee = None
        company = None

        if not problem_data or (
            'owner_id' not in problem_data and 'company_id' not in problem_data
        ):
            employee, company = await employee_of_company(return_company=True)

        owner_id = (
            problem_data.get('owner_id')
            if problem_data and 'owner_id' in problem_data
            else employee.id
        )
        company_id = (
            problem_data.get('company_id')
            if problem_data and 'company_id' in problem_data
            else company.id
        )

        default_data = {
            'name': 'проблема',
            'description': 'описание проблемы',
            'color': ProblemColor.RED,
            'type': ProblemType.B,
            'status': ProblemStatus.NEW,
            'owner_id': owner_id,
            'company_id': company_id,
        }
        if problem_data:
            default_data.update(problem_data)

        problem = await make_entry_in_table(async_session, default_data, Problem)

        if return_all_objects:
            return problem, employee, company
        return problem

    return _create_problem


@pytest_asyncio.fixture
async def message_feed_for_test(async_session: AsyncSession, problem_for_test):
    """
    Фикстура, создающая тред с возможностью изменения полей.

    Параметры:
        - message_feed_data (dict, optional): Данные для создания треда. Если не переданы,
          используются значения по умолчанию.
        - return_all_objects (bool, optional): Если True, возвращает кортеж
          (тред, проблема, сотрудник, компания).

    Возвращает:
        - MessageFeed: Объект созданного треда.
        - (MessageFeed, Problem, CompanyUser, Company): Если `return_all_objects=True`,
           возвращает кортеж (тред, проблема, сотрудник, компания).

    Примеры использования:
        # Создание треда только с обязательными полями
        message_feed = await message_feed_for_test()

        # Создание треда с кастомными параметрами
        message_feed = await message_feed_for_test({
            'text': 'Важное сообщение',
            'important': True
        })

        # Получение треда, проблемы, сотрудника и компании
        message_feed, problem, employee, company = await message_feed_for_test(
            return_all_objects=True
        )
    """

    async def _create_message_feed(message_feed_data=None, return_all_objects=False):
        """Функция-обёртка для создания треда с изменяемыми параметрами."""
        employee = None
        company = None
        problem = None

        if not message_feed_data or (
            'owner_id' not in message_feed_data and 'problem_id' not in message_feed_data
        ):
            problem, employee, company = await problem_for_test(return_all_objects=True)

        owner_id = (
            message_feed_data.get('owner_id')
            if message_feed_data and 'owner_id' in message_feed_data
            else employee.id
        )
        problem_id = (
            message_feed_data.get('problem_id')
            if message_feed_data and 'problem_id' in message_feed_data
            else problem.id
        )

        default_data = {
            'problem_id': problem_id,
            'owner_id': owner_id,
            'text': 'текст треда',
            'important': True,
        }
        if message_feed_data:
            default_data.update(message_feed_data)

        message_feed = await make_entry_in_table(async_session, default_data, MessageFeed)

        if return_all_objects:
            return message_feed, problem, employee, company
        return message_feed

    return _create_message_feed


@pytest_asyncio.fixture
async def comment_for_test(async_session: AsyncSession, message_feed_for_test):
    """
    Фикстура, создающая комментарий с возможностью изменения полей.

    Параметры:
        - comment_data (dict, optional): Данные для создания комментария. Если не переданы,
          используются значения по умолчанию.
        - return_all_objects (bool, optional): Если True, возвращает кортеж
          (комментарий, тред, проблема, сотрудник, компания).
        - with_like (bool, optional): Если True, создаётся лайк к коментарию.

    Возвращает:
        - CommentFeed: Объект созданного комментария.
        - (CommentFeed, MessageFeed, Problem, CompanyUser, Company):
            Если `return_all_objects=True`, возвращает кортеж
            (комментарий, тред, проблема, сотрудник, компания).

    Примеры использования:
        # Создание комментария только с обязательными полями
        comment = await comment_for_test()

        # Создание комментария с кастомными параметрами
        comment = await comment_for_test({
            'text': 'Важный комментарий',
            'message_id': 123
        })

        # Получение комментария, треда, проблемы, сотрудника и компании
        comment, message_feed, problem, employee, company = await comment_for_test(
            return_all_objects=True
        )
    """

    async def _create_comment(comment_data=None, return_all_objects=False, with_like=False):
        """Функция-обёртка для создания комментария с изменяемыми параметрами."""
        employee = None
        company = None
        problem = None
        message_feed = None

        if not comment_data or (
            'owner_id' not in comment_data and 'message_id' not in comment_data
        ):
            message_feed, problem, employee, company = await message_feed_for_test(
                return_all_objects=True
            )

        message_id = (
            comment_data.get('message_id')
            if comment_data and 'message_id' in comment_data
            else message_feed.id
        )
        owner_id = (
            comment_data.get('owner_id')
            if comment_data and 'owner_id' in comment_data
            else employee.id
        )

        default_data = {
            'text': 'текст комментария',
            'message_id': message_id,
            'owner_id': owner_id,
        }
        if comment_data:
            default_data.update(comment_data)

        comment = await make_entry_in_table(async_session, default_data, CommentFeed)
        if with_like:
            await async_session.execute(
                insert(AssociationUserComment).values(left_id=owner_id, right_id=comment.id)
            )
            await async_session.commit()

        if return_all_objects:
            return comment, message_feed, problem, employee, company
        return comment

    return _create_comment


@pytest_asyncio.fixture
async def meeting_for_test(async_session: AsyncSession, problem_for_test):
    """
    Фикстура, создающая встречу с возможностью изменения полей.

    Параметры:
        - meeting_data (dict, optional): Данные для создания встречи. Если не переданы,
          используются значения по умолчанию.
        - return_all_objects (bool, optional): Если True, возвращает кортеж
          (встреча, проблема, сотрудник, компания).

    Возвращает:
        - Meeting: Объект созданной встречи.
        - (Meeting, Problem, CompanyUser, Company): Если `return_all_objects=True`,
           возвращает кортеж (встреча, проблема, сотрудник, компания).

    Примеры использования:
        # Создание встречи только с обязательными полями
        meeting = await meeting_for_test()

        # Создание встречи с кастомными параметрами
        meeting = await meeting_for_test({
            'title': 'Важная встреча',
            'date_meeting': datetime.now().date(),
            'status': 'Завершена'
        })

        # Получение встречи, проблемы, сотрудника и компании
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)
    """

    async def _create_meeting(meeting_data=None, return_all_objects=False):
        """Функция-обёртка для создания встречи с изменяемыми параметрами."""
        employee = None
        company = None
        problem = None

        if not meeting_data or (
            'owner_id' not in meeting_data and 'problem_id' not in meeting_data
        ):
            problem, employee, company = await problem_for_test(return_all_objects=True)

        owner_id = (
            meeting_data.get('owner_id')
            if meeting_data and 'owner_id' in meeting_data
            else employee.id
        )
        problem_id = (
            meeting_data.get('problem_id')
            if meeting_data and 'problem_id' in meeting_data
            else problem.id
        )

        default_data = {
            'title': f'Test Meeting {uuid.uuid4().hex[:8]}',
            'date_meeting': (datetime.now() + timedelta(days=1)).date(),
            'status': 'Новая',
            'place': 'place',
            'problem_id': problem_id,
            'owner_id': owner_id,
        }
        if meeting_data:
            default_data.update(meeting_data)

        meeting = await make_entry_in_table(async_session, default_data, Meeting)

        if return_all_objects:
            return meeting, problem, employee, company
        return meeting

    return _create_meeting


@pytest_asyncio.fixture
async def department_for_test(async_session: AsyncSession, company_for_test):
    """
    Фикстура, создающая департамент с возможностью изменения полей.

    Параметры:
        - department_data (dict, optional): Данные для создания департамента.
          Если не переданы, используются значения по умолчанию.
        - return_company (bool, optional): Если True, возвращает кортеж
          (департамент, компания).

    Возвращает:
        - Department: Объект созданного департамента.
        - (Department, Company): Если return_company=True, возвращает кортеж
          (департамент, компания).

    Примеры использования:
        # Создание департамента только с обязательными полями:
        department = await department_for_test()

        # Создание департамента с кастомными параметрами:
        department = await department_for_test({'name': 'Отдел продаж'})

        # Получение департамента и компании:
        department, company = await department_for_test(return_company=True)
    """

    async def _create_department(department_data=None, return_company=False):
        company = None

        if not department_data or 'company_id' not in department_data:
            company = await company_for_test()

        company_id = company.id if company else department_data.get('company_id')

        default_data = {
            'name': f'Department {uuid.uuid4().hex[:8]}',
            'company_id': company_id,
            'slug': slugify(f'Department {uuid.uuid4().hex[:8]}'),
        }

        if department_data:
            default_data.update(department_data)
        department = await make_entry_in_table(async_session, default_data, Department)

        if return_company:
            return department, company
        return department

    return _create_department
