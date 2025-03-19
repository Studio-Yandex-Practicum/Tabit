import asyncio
from random import choice
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.company_user_factories import CompanyUserFactory
from fake_data_factories.constants import FAKER_MESSAGE_FEEDS_COUNT
from fake_data_factories.problem_factory import create_problems
from src.database.sc_db_session import sc_session
from src.problems.models.message_models import MessageFeed


class MessageFeedFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации ленты сообщений.

    Поля:
        - `problem_id`: Обязательное поле. \
            Должен быть создан объект `Problem`, чтобы передать полю id.
        - `owner_id`: Обязательное поле. \
            Должен быть создан объект `UserTabit`, чтобы передать полю id (типа uuid).
        - `text`: Обязательное поле. Генерируется `Faker`.
        - `important`: Обязательное поле. Генерируется случайным выбором из [True, False].
    """

    problem_id: int
    owner_id: UUID
    text: factory.Faker = factory.Faker('text', locale='ru_RU')
    important: factory.LazyFunction = factory.LazyFunction(lambda: choice([True, False]))

    class Meta:
        model = MessageFeed
        sqlalchemy_session = sc_session


async def create_message_feeds(
    count: int = FAKER_MESSAGE_FEEDS_COUNT, **kwargs
) -> list[MessageFeed]:
    """
    Создать запись(-и) в таблицу объекта `MessageFeed`.

    Если функция запускается напрямую из текущего модуля, для этих лент сообщений создаются:
    - проблема (id проблемы передаётся в фабрику);
    - компания (id компании передаётся в фабрику создания пользователя);
    - пользователь Tabit (uuid пользователя передаётся в фабрику).

    Если функция запускается через импорт, в неё можно передать именованный аргумент \
    `owner_id`. Если не передать, запустится фабрика CompanyUserFactory \
        с предварительным запуском фабрики CompanyFactory, а также запустится фабрика \
        создания проблемы от авторства созданного фабрикой пользователя.

    Функция возвращает список лент сообщений.
    """
    if 'owner_id' not in kwargs:
        company = await CompanyFactory.create()
        user_tabit = await CompanyUserFactory.create(company_id=company.id)
        kwargs['owner_id'] = user_tabit.id
        problem = (await create_problems(count=1, owner_id=user_tabit.id))[0]
        kwargs['problem_id'] = problem.id
    message_feeds = await MessageFeedFactory.create_batch(count, **kwargs)
    cprint(
        f'Создано {count} лент сообщений по проблеме c id: {kwargs["problem_id"]} '
        f'от пользователя с id: {kwargs["owner_id"]}',
        'green',
    )
    return message_feeds


if __name__ == '__main__':
    asyncio.run(create_message_feeds())
