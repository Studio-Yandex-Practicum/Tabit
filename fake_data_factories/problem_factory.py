import asyncio
from random import choice
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from config.constants.fake_data_factories import ColorCPrint, Default, Faker
from fake_data_factories.association_user_problem_factory import (
    create_user_problem_associations,
)
from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import Problem, ProblemColor, ProblemStatus, ProblemType


class ProblemFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных проблемы.

    Поля:
        - `name`: Обязательное поле. \
            Генерируется случайным выбором из `Default.PROBLEM_NAMES`.
        - `description`: Опциональное поле.\
            Генерируется случайным выбором из `Default.PROBLEM_DESCRIPTIONS`.
        - `company_id`: Обязательное поле. \
            Должен быть создан объект Company, чтобы передать полю slug.
        - `color`: Обязательное поле. Генерируется случайным выбором из `ProblemColor`.
        - `type`: Обязательное поле. Генерируется случайным выбором из `ProblemType`.
        - `status`: Обязательное поле. Генерируется случайным выбором из `ProblemStatus`.
        - `owner_id`: Обязательное поле. \
            Должен быть создан объект `CompanyUser`, чтобы передать полю id (типа uuid).
    """

    name: factory.LazyFunction = factory.LazyFunction(lambda: choice(Default.PROBLEM_NAMES))
    description: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(Default.PROBLEM_DESCRIPTIONS)
    )
    company_id: int
    color: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(ProblemColor)))
    type: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(ProblemType)))
    status: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(ProblemStatus)))
    owner_id: UUID

    class Meta:
        model = Problem
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_problems(count: int = Faker.PROBLEMS_COUNT, **kwargs) -> list[Problem]:
    """
    Создать запись(-и) в таблицу объекта `Problem`.

    Если функция запускается напрямую из текущего модуля, для этих проблем создаются:
    - компания (id компании передаётся в фабрику);
    - пользователь Tabit (uuid пользователя передаётся в фабрику).

    Если функция запускается через импорт, в неё можно передать именованные аргументы:
    - `company_id` (если не передать, запустится фабрика создания компании);
    - `owner_id` (если не передать, запустится фабрика создания пользователей компании).
    Примечание: если какой-то из именованных параметров не передался, \
        работает так, как если не передавать именованные аргументы.

    Функция вызывает фабрику связей пользователь-проблема.

    Функция возвращает список проблем.
    """
    if 'owner_id' not in kwargs or 'company_id' not in kwargs:
        company = next(iter(await create_companies(count=1)), None)
        kwargs['company_id'] = company.id
        user_tabit = next(iter(await create_company_users(count=1, company_id=company.id)), None)
        kwargs['owner_id'] = user_tabit.id
    problems = await ProblemFactory.create_batch(count, **kwargs)
    cprint(
        f'Создано {count} проблем компании cо id: {kwargs["company_id"]} '
        f'от пользователя с id: {kwargs["owner_id"]}',
        ColorCPrint.green,  # type: ignore
    )
    await create_user_problem_associations(
        user_id=kwargs['owner_id'], problem_ids=[problem.id for problem in problems]
    )
    return problems


if __name__ == '__main__':
    asyncio.run(create_problems())
