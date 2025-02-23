import asyncio
import random
from enum import Enum
from typing import Optional

import factory
from termcolor import cprint

from constants import FAKER_USER_COUNT
from fake_data_factories.base_user_factory import BaseUserFactory
from fake_data_factories.company_factories import CompanyFactory
from src.database.alembic_models import UserTabit
from src.database.sc_db_session import sc_session


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

    class Meta:
        model = UserTabit
        sqlalchemy_session = sc_session

    employee_position: str = factory.LazyFunction(lambda: random.choice(list(PositionEnum)))
    current_department_id: Optional[int] = None
    role: str = 'Сотрудник'

    @factory.lazy_attribute
    async def company_id(self):
        company = await CompanyFactory.create()
        return company.id

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if kwargs.get('company_id') is None:
            raise ValueError('Ошибка: company_id не передан в фабрику TabitUserFactory.')
        return super()._create(model_class, *args, **kwargs)


async def create_company_users(count: int = FAKER_USER_COUNT, company_id=None) -> None:
    await CompanyUserFactory.create_batch(count, company_id=company_id)
    cprint(f'Создано {count} Companies', 'green')


if __name__ == '__main__':
    asyncio.run(create_company_users())
