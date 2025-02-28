import asyncio
import random
from enum import Enum
from typing import Optional

import factory
from termcolor import cprint

from constants import AMOUNT_OF_ADMIN, FAKER_USER_COUNT
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

    employee_position: str = factory.LazyFunction(lambda: random.choice(list(PositionEnum)))
    current_department_id: Optional[int] = None
    role: str = 'Сотрудник'
    company_id: int

    class Meta:
        model = UserTabit
        sqlalchemy_session = sc_session


async def create_company_users(count: int = FAKER_USER_COUNT, **kwargs) -> None:
    """
    Функция для наполнения таблицы бд UserTabit.
    Для компании создается 1 админ, и все остальные простые сотрудники.
    Если функция запускается напрямую из текущего модуля, для этих департаментов создается
    компания, id этой компании передается в фабрику.
    Если функция запускается через импорт, в неё нужно передать именованный аргумент company_id,
    чтобы он попал в kwargs для заполнения обязательного поля фабрики company_id.
    """
    if __name__ == '__main__':
        company = await CompanyFactory.create()
        kwargs['company_id'] = company.id
    await CompanyUserFactory.create_batch(AMOUNT_OF_ADMIN, role='Админ', **kwargs)
    await CompanyUserFactory.create_batch(count - AMOUNT_OF_ADMIN, **kwargs)
    cprint(f'Создано {count} работников компании c id: {kwargs["company_id"]}', 'green')


if __name__ == '__main__':
    asyncio.run(create_company_users())
