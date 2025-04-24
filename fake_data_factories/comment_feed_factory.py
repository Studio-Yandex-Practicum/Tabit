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
    FAKER_COMMENT_WORDS_COUNT,
    FAKER_MAX_COMMENT_RATING,
    FAKER_MIN_COMMENT_RATING,
    ColorCPrint,
)
from fake_data_factories.message_feed_factory import create_message_feeds
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import CommentFeed, CompanyUser, MessageFeed


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
        'sentence', locale='ru_RU', nb_words=FAKER_COMMENT_WORDS_COUNT, variable_nb_words=True
    )
    rating: int = factory.Faker(
        'random_int', min=FAKER_MIN_COMMENT_RATING, max=FAKER_MAX_COMMENT_RATING
    )

    class Meta:
        model = CommentFeed
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_comments(count=FAKER_COMMENT_COUNT, **kwargs) -> None:
    """
    Функция для пакетного создания комментариев.

    Функция создает указанное количество комментариев. Можно передать следуюшие аргументы:
        count: Количество комментариев для создания.
        owner_id: ID автора комментариев.
        message_id: ID треда, к которому относится комментарий.

    Если не указать owner_id, то создается 5 новых пользователей в той же компании что и автор
    сообщения, и каждый комментарий будет создан от имени нового автора.
    """
    if 'message_id' not in kwargs:
        message = next(iter(await create_message_feeds(count=1)), None)
        kwargs['message_id'] = message.id
    else:
        result = await sc_session.execute(
            select(MessageFeed).where(MessageFeed.id == kwargs['message_id'])
        )
        message = result.scalar()
    if 'owner_id' not in kwargs:
        result = await sc_session.execute(
            select(CompanyUser).where(CompanyUser.id == message.owner_id)
        )
        message_owner = result.scalar()
        comment_owners = await create_company_users(
            count=count, company_id=message_owner.company_id
        )
        comment_owners_ids = [owner.id for owner in comment_owners]
        comments = [
            await CommentFeedFactory.create(owner_id=owner_id, **kwargs)
            for owner_id in comment_owners_ids
        ]
        cprint(
            f'Создано {count} комментариев в треде c id: {kwargs["message_id"]}',
            ColorCPrint.green,  # type: ignore
        )
        for i in range(count):
            await create_user_comment_associations(
                user_id=comment_owners_ids[i], comment_ids=[comments[i].id]
            )
    else:
        comments = await CommentFeedFactory.create_batch(size=2, **kwargs)
        cprint(
            f'Создано {count} комментариев в треде c id: {kwargs["message_id"]}',
            ColorCPrint.green,  # type: ignore
        )
        await create_user_comment_associations(
            user_id=kwargs['owner_id'], comment_ids=[comment.id for comment in comments]
        )


if __name__ == '__main__':
    asyncio.run(create_comments())
