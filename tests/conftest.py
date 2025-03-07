import uuid
from collections.abc import AsyncGenerator
from datetime import timedelta
from typing import Any

import pytest
import pytest_asyncio
from fastapi_users.password import PasswordHelper
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.companies.models.models import Company
from src.database.db_depends import get_async_session
from src.database.models import BaseTabitModel as Base
from src.main import app_v1
from src.problems.models import AssociationUserComment, CommentFeed, MessageFeed, Problem
from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem
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

    async def _create_employee(user_data=None, company=None):
        """Функция-обёртка для пользователя тестовой компании с изменяемыми параметрами."""
        if not company:
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


# Фикстуры для тестов problem_feeds.py
@pytest_asyncio.fixture
async def company_1(company_for_test):
    """Фикстура для создания компании №1 в таблице company."""
    return await company_for_test({'name': 'Zorg', 'slug': 'Zorg', 'is_active': True})


@pytest_asyncio.fixture
async def company_2(company_for_test):
    """Фикстура для создания компании №2 в таблице company."""
    return await company_for_test(
        {'name': 'Anaheim Electronics', 'slug': 'Anaheim_Electronics', 'is_active': True}
    )


@pytest_asyncio.fixture
async def employee_1_company_1(company_1, employee_of_company):
    """Фикстура для создания пользователя 1 от компании 1 в таблице usertabit."""
    return await employee_of_company({'name': 'Брюс', 'surname': 'Ли'}, company_1)


@pytest_asyncio.fixture
async def employee_2_company_1(company_1, employee_of_company):
    """Фикстура для создания пользователя 2 от компании 1 в таблице usertabit."""
    return await employee_of_company({'name': 'Ким', 'surname': 'Кицураги'}, company_1)


@pytest_asyncio.fixture
async def employee_3_company_2(company_2, employee_of_company):
    """Фикстура для создания пользователя 3 от компании 2 в таблице usertabit."""
    return await employee_of_company({'name': 'Нейтан', 'surname': 'Дрейк'}, company_2)


@pytest_asyncio.fixture
async def employee_1_company_1_token(get_token_for_user, employee_1_company_1):
    """
    Фикстура для получения заголовков авторизации пользователя 2 от компании 1 c access-token.
    """
    return await get_token_for_user(employee_1_company_1)


@pytest_asyncio.fixture
async def employee_2_company_1_token(get_token_for_user, employee_2_company_1):
    """
    Фикстура для получения заголовков авторизации пользователя 2 от компании 1 c access-token.
    """
    return await get_token_for_user(employee_2_company_1)


@pytest_asyncio.fixture
async def employee_3_company_2_token(get_token_for_user, employee_3_company_2):
    """
    Фикстура для получения заголовков авторизации пользователя 3 от компании 2 c access-token.
    """
    return await get_token_for_user(employee_3_company_2)


@pytest_asyncio.fixture
async def problem_for_test(async_session: AsyncSession):
    async def _create_problem(employee, problem_data=None):
        problem_obj = {
            'name': 'проблема',
            'description': 'описание проблемы',
            'color': ColorProblem.RED,
            'type': TypeProblem.B,
            'status': StatusProblem.NEW,
            'owner_id': employee.id,
            'company_id': employee.company_id,
        }
        if problem_data:
            problem_obj.update(problem_data)
        return await make_entry_in_table(async_session, problem_obj, Problem)

    return _create_problem


@pytest_asyncio.fixture
async def problem_1(employee_1_company_1, problem_for_test):
    """Фикстура для создания проблемы 1 от пользователя 1 компании 1."""
    return await problem_for_test(employee_1_company_1, {'name': 'проблема 1'})


@pytest_asyncio.fixture
async def problem_2(employee_3_company_2, problem_for_test):
    """Фикстура для создания проблемы 2 от пользователя 3 компании 2."""
    return await problem_for_test(employee_3_company_2, {'name': 'проблема 2'})


@pytest_asyncio.fixture
async def message_feed_for_test(async_session: AsyncSession, problem_for_test):
    async def _create_message_feed(employee, message_feed_data=None, problem=None):
        if not problem:
            problem = await problem_for_test(employee)
        message_feed_obj = {
            'problem_id': problem.id,
            'owner_id': employee.id,
            'text': 'текст треда',
            'important': True,
        }
        if message_feed_data:
            message_feed_obj.update(message_feed_data)
        return await make_entry_in_table(async_session, message_feed_obj, MessageFeed)

    return _create_message_feed


@pytest_asyncio.fixture
async def message_feed_1(employee_1_company_1, message_feed_for_test):
    """Фикстура для создания треда 1 для проблемы 1."""
    return await message_feed_for_test(employee_1_company_1, {'text': 'тред 1'})


@pytest_asyncio.fixture
async def message_feed_2(employee_3_company_2, message_feed_for_test):
    """Фикстура для создания треда 2 для проблемы 2."""
    return await message_feed_for_test(employee_3_company_2, {'text': 'тред 2'})


@pytest_asyncio.fixture
async def message_feed_3(employee_1_company_1, message_feed_for_test, problem_1):
    """Фикстура для создания треда 3 для проблемы 1."""
    return await message_feed_for_test(employee_1_company_1, {'text': 'тред 3'}, problem_1)


@pytest_asyncio.fixture
async def ten_message_feeds(async_session: AsyncSession, problem_1, employee_1_company_1):
    """Фикстура для создания списка тредов."""
    message_feed_data = [
        MessageFeed(problem_id=problem_1.id, owner_id=employee_1_company_1.id, text=f'тред {i}')
        for i in range(10)
    ]
    async_session.add_all(message_feed_data)
    await async_session.commit()
    result = await async_session.execute(select(MessageFeed))
    return result.all()


@pytest_asyncio.fixture
async def comment_for_test(async_session: AsyncSession, message_feed_for_test):
    async def _create_comment(employee, comment_data=None, message_feed=None):
        if not message_feed:
            message_feed = await message_feed_for_test(employee)
        comment_obj = {
            'text': 'текст комментария',
            'message_id': message_feed.id,
            'owner_id': employee.id,
        }
        if comment_data:
            comment_obj.update(comment_data)
        return await make_entry_in_table(async_session, comment_obj, CommentFeed)

    return _create_comment


@pytest_asyncio.fixture
async def comment_1(employee_1_company_1, comment_for_test):
    """Фикстура для создания комментария 1 к треду 1 от пользователя 1"""
    return await comment_for_test(employee_1_company_1, {'text': 'комментарий 1'})


@pytest_asyncio.fixture
async def liked_comment_1(async_session, employee_2_company_1, comment_1):
    """Фикстура для лайка комментария comment_1."""
    like_obj = AssociationUserComment(left_id=employee_2_company_1.id, right_id=comment_1.id)
    async_session.add(like_obj)
    comment_1.rating += 1
    async_session.add(comment_1)
    await async_session.commit()
    await async_session.refresh(comment_1)
    return comment_1


@pytest_asyncio.fixture
async def ten_comments(async_session: AsyncSession, message_feed_1, employee_1_company_1):
    """Фикстура для создания списка комментариев."""
    comments_data = [
        CommentFeed(
            message_id=message_feed_1.id, owner_id=employee_1_company_1.id, text=f'текст {i}'
        )
        for i in range(10)
    ]
    async_session.add_all(comments_data)
    await async_session.commit()
    result = await async_session.execute(select(CommentFeed))
    return result.all()
