import asyncio
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy import select
from termcolor import cprint

from fake_data_factories.association_user_comment_factory import create_user_comment_associations
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import (
    FAKER_COMMENT_COUNT,
    FAKER_MAX_COMMENT_RATING,
    FAKER_MIN_COMMENT_RATING,
    MAX_COMMENT_WORDS_COUNT,
)
from fake_data_factories.message_feed_factory import create_message_feeds
from src.database.sc_db_session import sc_session
from src.problems.models.message_models import CommentFeed, MessageFeed
from src.users.models.models import UserTabit


class CommentFeedFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для для создания тестовых данных комментариев.

    Поля:
        message_id: Идентификатор треда, к которому относится комментарий.
        owner_id: Автор комментария. Внешний ключ.
        text: Текст комментария.
        rating: Рейтинг комментария
    """

    message_id: int
    owner_id: UUID
    text: str = factory.Faker(
        'sentence', locale='ru_RU', nb_words=MAX_COMMENT_WORDS_COUNT, variable_nb_words=True
    )
    rating: int = factory.Faker(
        'random_int', min=FAKER_MIN_COMMENT_RATING, max=FAKER_MAX_COMMENT_RATING
    )

    class Meta:
        model = CommentFeed
        sqlalchemy_session = sc_session


async def create_comments(count=FAKER_COMMENT_COUNT, **kwargs) -> None:
    """
    Функция для пакетного создания комментариев.

    Функция создает указанное количество комментариев. Можно передать следуюшие аргументы:
        count: Количество комментариев для создания.
        owner_id: ID автора комментариев.
        message_id: ID треда, к которому относится комментарий.
    """
    if 'message_id' not in kwargs:
        message = next(iter(await create_message_feeds(count=1)), None)
        kwargs['message_id'] = message.id
    else:
        query = await sc_session.execute(
            select(MessageFeed).where(MessageFeed.id == kwargs['message_id'])
        )
        message = query.scalar()
    if 'owner_id' not in kwargs:
        query = await sc_session.execute(select(UserTabit).where(UserTabit.id == message.owner_id))
        message_owner = query.scalar()
        owner = next(
            iter(await create_company_users(count=1, company_id=message_owner.company_id)), None
        )
        kwargs['owner_id'] = owner.id
    comments = await CommentFeedFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} комментариев в треде c id: {kwargs["message_id"]}', 'green')
    await create_user_comment_associations(
        user_id=kwargs['owner_id'], comment_ids=[comment.id for comment in comments]
    )


if __name__ == '__main__':
    asyncio.run(create_comments())
