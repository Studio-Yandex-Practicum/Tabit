import asyncio

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import FAKER_VOTING_FEEDS_COUNT, ColorCPrint
from fake_data_factories.message_feed_factory import create_message_feeds
from fake_data_factories.problem_factory import create_problems
from fake_data_factories.utils import start_and_end
from src.constants import LENGTH_SMALL_NAME
from src.database.sc_db_session import sc_session
from src.problems.models.message_models import VotingFeed


class VotingFeedFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации ленты голосования.

    Поля:
        - `message_id`: Обязательное поле. \
            Должен быть создан объект `MessageFeed`, чтобы передать полю id.
        - `name`: Обязательное поле. Генерируется `Faker`. \
            Длина поля ограничена константой LENGTH_SMALL_NAME.
    """

    message_id: int
    name: factory.Faker = factory.Faker('text', locale='ru_RU', max_nb_chars=LENGTH_SMALL_NAME)

    class Meta:
        model = VotingFeed
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_voting_feeds(count: int = FAKER_VOTING_FEEDS_COUNT, **kwargs) -> list[VotingFeed]:
    """
    Создать запись(-и) в таблицу объекта `VotingFeed`.

    Если функция запускается напрямую из текущего модуля, \
        для этих вариантов голосований создаются:
    - компания (id компании передаётся в фабрику создания пользователя, \
        slug компании передаётся в фабрику создания проблемы);
    - пользователь Tabit (uuid пользователя передаётся в фабрику создания проблемы и \
        в фабрику создания ленты сообщений);
    - проблема (id проблемы передаётся в фабрику создания ленты сообщений);
    - лента сообщений (id ленты сообщений передаётся в фабрику).

    Если функция запускается через импорт, в неё можно передать именованный аргумент \
    `message_id`. Если не передать, то запускается, как если бы запускалась из текущего модуля.

    Функция возвращает список вариантов голосования.
    """
    if 'message_id' not in kwargs:
        company = next(iter(await create_companies(count=1)), None)
        user_tabit = next(iter(await create_company_users(count=1, company_id=company.id)), None)
        problem = next(
            iter(
                await create_problems(count=1, owner_id=user_tabit.id, company_slug=company.slug)
            ),
            None,
        )
        message_feed = next(
            iter(
                await create_message_feeds(count=1, problem_id=problem.id, owner_id=user_tabit.id)
            ),
            None,
        )
        kwargs['message_id'] = message_feed.id
    voting_feeds = await VotingFeedFactory.create_batch(count, **kwargs)
    cprint(
        f'Создано {count} вариантов голосования для сообщения c id: {kwargs["message_id"]}',
        ColorCPrint.green,  # type: ignore
    )
    return voting_feeds


if __name__ == '__main__':
    asyncio.run(create_voting_feeds())
