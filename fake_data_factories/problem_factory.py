import asyncio
from random import choice
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.company_user_factories import CompanyUserFactory
from fake_data_factories.constants import (
    DEFAULT_PROBLEM_DESCRIPTIONS,
    DEFAULT_PROBLEM_NAMES,
    FAKER_PROBLEMS_COUNT,
)
from src.database.sc_db_session import sc_session
from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem
from src.problems.models.problem_models import Problem


class ProblemFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных проблемы.

    Поля:
        - `name`: Обязательное поле. \
            Генерируется случайным выбором из `DEFAULT_PROBLEM_NAMES`.
        - `description`: Опциональное поле.\
            Генерируется случайным выбором из `DEFAULT_PROBLEM_DESCRIPTIONS`.
        - `company_slug`: Обязательное поле. \
            Должен быть создан объект Company, чтобы передать полю slug.
        - `color`: Обязательное поле. Генерируется случайным выбором из `ColorProblem`.
        - `type`: Обязательное поле. Генерируется случайным выбором из `TypeProblem`.
        - `status`: Обязательное поле. Генерируется случайным выбором из `StatusProblem`.
        - `owner_id`: Обязательное поле. \
            Должен быть создан объект `UserTabit`, чтобы передать полю id (типа uuid).
    """

    name: factory.LazyFunction = factory.LazyFunction(lambda: choice(DEFAULT_PROBLEM_NAMES))
    description: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(DEFAULT_PROBLEM_DESCRIPTIONS)
    )
    company_slug: str
    color: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(ColorProblem)))
    type: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(TypeProblem)))
    status: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(StatusProblem)))
    owner_id: UUID

    class Meta:
        model = Problem
        sqlalchemy_session = sc_session


async def create_problems(count: int = FAKER_PROBLEMS_COUNT, **kwargs) -> list[Problem]:
    """
    Создать запись(-и) в таблицу объекта `Problem`.

    Если функция запускается напрямую из текущего модуля, для этих проблем создаются:
    - компания (slug компании передаётся в фабрику);
    - пользователь Tabit (uuid пользователя передаётся в фабрику).

    Если функция запускается через импорт, в неё можно передать именованные аргументы:
    - `company_slug` (если не передать, запустится фабрика `CompanyFactory`);
    - `owner_id` (если не передать, запустится фабрика `CompanyUserFactory`).
    Примечание: если какой-то из именованных параметров не передался, \
        работает так, как если не передавать именованные аргументы.

    Функция возвращает список проблем.
    """
    if 'owner_id' not in kwargs or 'company_slug' not in kwargs:
        company = await CompanyFactory.create()
        kwargs['company_slug'] = company.slug
        user_tabit = await CompanyUserFactory.create(company_id=company.id)
        kwargs['owner_id'] = user_tabit.id
    problems = await ProblemFactory.create_batch(count, **kwargs)
    cprint(
        f'Создано {count} проблем компании cо slug: {kwargs["company_slug"]} '
        f'от пользователя с id: {kwargs["owner_id"]}',
        'green',
    )
    return problems


if __name__ == '__main__':
    asyncio.run(create_problems())
