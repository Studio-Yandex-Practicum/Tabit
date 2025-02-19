import asyncio
import random
from enum import Enum
from typing import Optional

import factory
from sqlalchemy import exists, select

from src.api.v1.auth.managers import UserManager, get_user_db
from src.companies.factories.company_factory import create_company
from src.companies.models.models import Company
from src.database.db_depends import get_async_session
from src.tabit_management.schemas.admin_company import (
    CompanyAdminCreateSchema,
)
from src.users.factories.base_user_factory import BaseUserFactory
from src.users.schemas.user import UserCreateSchema


async def get_user_manager_instance(session) -> UserManager:
    """Создаёт UserManager внутри активной сессии."""
    async for user_db in get_user_db(session):  # anext() не пропускает ruff
        return UserManager(user_db)
    raise ValueError('get_user_db(session) не вернул объект')


class PositionEnum(str, Enum):
    ASSISTANT_HEAD_OF_SECURITY = 'Помощник начальника службы безопасности'
    HEAD_OF_SECURITY = 'Начальник службы безопасности'
    DEVELOPMENT_MANAGER = 'Менеджер по развитию'


class CompanyUserFactory(BaseUserFactory):
    """
    Фабрика генерации данных для сотрудника компании.

    Поля:
        1. employee_position: Выбирается случайным образом из PositionEnum класса.
        2. company_id: Обязательное поле. По умолчанию None, номер компании присваивается
        сотруднику в функции создания пользователя create_tabit_user.
        3. current_department_id: По умолчанию None, присвиваетется сотруднику в функции создания
        пользователя create_tabit_user.
        4. role: По умолчанию 'Сотрудник', можно подставить 'Админ' при создании сотрудника.
    """

    employee_position: str = factory.LazyFunction(lambda: random.choice(list(PositionEnum)))
    company_id = None
    current_department_id: Optional[int] = None
    role: str = 'Сотрудник'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs.get('company_id') is None:
            raise ValueError('Ошибка: company_id не передан в фабрику TabitUserFactory.')
        return super()._create(model_class, *args, **kwargs)


async def create_tabit_user(
    amount: int = 1, company_id: int | None = None, is_admin: bool = False
):
    async for session in get_async_session():
        try:
            if not company_id:
                new_company = await create_company(session=session)
                company_id = new_company.id
            else:
                company_exists = await session.execute(
                    select(exists().where(Company.id == company_id))
                )
                if not company_exists.scalar():
                    raise ValueError(f'Компания с ID {company_id} отсутствует в бд.')

            user_manager = await get_user_manager_instance(session)
            user_schema = CompanyAdminCreateSchema if is_admin else UserCreateSchema
            for _ in range(amount):
                tabit_user_data = CompanyUserFactory.build(company_id=company_id)
                print(tabit_user_data['company_id'])
                tabit_user_scheme_data = user_schema(**tabit_user_data)
                new_tabit_user = await user_manager.create(tabit_user_scheme_data)
                print(f'Создан пользователь: {new_tabit_user.name}')
        except Exception as e:
            print(f'Ошибка: {e}')
            await session.rollback()
        finally:
            await session.close()


if __name__ == '__main__':
    asyncio.run(create_tabit_user(amount=1))
