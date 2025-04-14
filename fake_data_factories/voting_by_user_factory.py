import asyncio
from random import sample
from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.message_feed_factory import create_message_feeds
from fake_data_factories.problem_factory import create_problems
from fake_data_factories.utils import start_and_end
from fake_data_factories.voting_feed_factory import create_voting_feeds
from src.core.database.sc_db_session import sc_session
from src.models import VotingByUser


class VotingByUserFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации голосования пользователя.

    Поля:
        - `user_id`: Обязательное поле. \
            Должен быть создан объект `CompanyUser`, чтобы передать полю uuid.
        - `voting_id`: Обязательное поле. \
            Должен быть создан объект `VotingFeed`, чтобы передать полю id.
    """

    user_id: UUID
    voting_id: int

    class Meta:
        model = VotingByUser
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_user_voting_associations(
    user_id: UUID, voting_ids: list[int]
) -> list[VotingByUser]:
    """
    Создать запись(-и) в таблицу объекта `VotingByUser`.

    Поля:
        - `user_id`: uuid пользователя Tabit;
        - `voting_ids`: список id голосований пользователя.

    Функция возвращате список созданных записей.
    """
    user_voting_associations = []
    for voting_id in voting_ids:
        user_voting_associations.append(
            await VotingByUserFactory.create(user_id=user_id, voting_id=voting_id)
        )
    cprint(
        f'Создано {len(user_voting_associations)} голосов пользователя с id: {user_id}',
        'green',
    )
    return user_voting_associations


@start_and_end(__name__)
async def create_voting_by_user(count: int = 1, **kwargs) -> list[VotingByUser]:
    """
    Создать запись(-и) в таблицу объекта `VotingByUser`.

    Если функция запускается напрямую из текущего модуля, \
        для этих голосов пользователя создаются:
    - компания (id компании передаётся в фабрику создания пользователя, \
        slug компании передаётся в фабрику создания проблемы);
    - пользователь Tabit (uuid пользователя передаётся в фабрику создания проблемы, \
        в фабрику создания ленты сообщений и в текущую фабрику);
    - проблема (id проблемы передаётся в фабрику создания ленты сообщений);
    - лента сообщений (id ленты сообщений передаётся в фабрику создания вариантов голосования);
    - варианты голосования к сообщению (id вариантов голосов передаётся в фабрику).

    Если функция запускается через импорт, в неё можно передать именованный аргумент \
    `user_id`. Если не передать, то запускается, как если бы запускалась из текущего модуля.

    Функция возвращает список вариантов голосования.
    """
    if 'user_id' not in kwargs:
        company = next(iter(await create_companies(count=1)), None)
        user_tabit = next(iter(await create_company_users(count=1, company_id=company.id)), None)
        kwargs['user_id'] = user_tabit.id
        problem = next(
            iter(
                await create_problems(
                    count=1, owner_id=kwargs['user_id'], company_slug=company.slug
                )
            ),
            None,
        )
        message_feed = next(
            iter(
                await create_message_feeds(
                    count=1, problem_id=problem.id, owner_id=kwargs['user_id']
                )
            ),
            None,
        )
        voting_feeds = await create_voting_feeds(message_id=message_feed.id)
        voting_ids = [voting_feed.id for voting_feed in voting_feeds]
    return await create_user_voting_associations(
        user_id=kwargs['user_id'],
        voting_ids=sample(voting_ids, count),
    )


if __name__ == '__main__':
    asyncio.run(create_voting_by_user())
