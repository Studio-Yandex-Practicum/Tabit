import asyncio
import random
from enum import Enum
from typing import Optional

import factory
from termcolor import cprint

from fake_data_factories.base_user_factory import BaseUserFactory
from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.constants import ColorCPrintConstants, FakerConstants
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import CompanyUser


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
        4. role: По умолчанию 'Сотрудник', можно подставить 'Модератор' при создании сотрудника.
    """

    employee_position: factory.LazyFunction = factory.LazyFunction(
        lambda: random.choice(list(PositionEnum))
    )
    current_department_id: Optional[int] = None
    role: str = 'Сотрудник'
    company_id: int

    class Meta:
        model = CompanyUser
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_company_users(
    count: int = FakerConstants.USER_COUNT,
    **kwargs,
) -> list[CompanyUser]:
    """
    Функция для наполнения таблицы бд CompanyUser.
    Для компании создается 1 админ, и все остальные простые сотрудники.
    Если функция запускается напрямую из текущего модуля, для этих департаментов создается
    компания, id этой компании передается в фабрику.
    Если функция запускается через импорт, в неё нужно передать именованный аргумент company_id,
    чтобы он попал в kwargs для заполнения обязательного поля фабрики company_id.

    Возвращает список созданных пользователей.
    """
    company_users: list[CompanyUser] = []
    if __name__ == '__main__':
        company_users = await CompanyFactory.create()
        kwargs['company_id'] = company_users.id
    company_users += await CompanyUserFactory.create_batch(
        FakerConstants.AMOUNT_OF_MODERATORS, role='Модератор', **kwargs
    )
    company_users += await CompanyUserFactory.create_batch(
        count - FakerConstants.AMOUNT_OF_MODERATORS, **kwargs
    )
    cprint(
        f'Создано {count} работников компании c id: {kwargs["company_id"]}',
        ColorCPrintConstants.green,
    )
    return company_users


if __name__ == '__main__':
    asyncio.run(create_company_users())
