import asyncio
from random import randint
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy import select
from termcolor import cprint

from fake_data_factories.association_user_comment_factory import create_user_comment_associations
from fake_data_factories.company_user_factories import CompanyUserFactory, create_company_users
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
    rating: int

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

    Если не указать owner_id, то создаются новые пользователи, количество которых равно count,в той
    же компании что и автор сообщения, и каждый комментарий будет создан от имени нового автора.
    Если указать owner_id, то будет созданы комментарии в количестве равным count.
    Каждому комментарию присваивается рандомный рейтинг в диапазоне
    [FAKER_MIN_COMMENT_RATING, FAKER_MAX_COMMENT_RATING]. Для полученного числа создаются новые
    пользователи в той же компании и записи AssociationUserComment (лайки).
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
        for owner_id in comment_owners_ids:
            kwargs['rating'] = randint(FAKER_MIN_COMMENT_RATING, FAKER_MAX_COMMENT_RATING)
            comment = await CommentFeedFactory.create(owner_id=owner_id, **kwargs)
            for _ in range(kwargs['rating']):
                user = await CompanyUserFactory.create(company_id=message_owner.company_id)
                await create_user_comment_associations(user_id=user.id, comment_ids=[comment.id])
        cprint(
            f'Создано {count} комментариев в треде c id: {kwargs["message_id"]}',
            ColorCPrint.green,  # type: ignore
        )
    else:
        user_owner = await sc_session.execute(
            select(CompanyUser).filter(CompanyUser.id == kwargs['owner_id'])
        )
        user_owner = user_owner.scalar()
        for _ in range(count):
            kwargs['rating'] = randint(FAKER_MIN_COMMENT_RATING, FAKER_MAX_COMMENT_RATING)
            comment = await CommentFeedFactory.create(**kwargs)
            for _ in range(kwargs['rating']):
                user = await CompanyUserFactory.create(company_id=user_owner.company_id)
                await create_user_comment_associations(user_id=user.id, comment_ids=[comment.id])
        cprint(
            f'Создано {count} комментариев в треде c id: {kwargs["message_id"]}',
            ColorCPrint.green,  # type: ignore
        )


if __name__ == '__main__':
    asyncio.run(create_comments())
