import asyncio
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy import func, select
from termcolor import cprint

from constants import FAKER_USER_TAGS_COUNT
from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from src.database.sc_db_session import sc_session
from src.users.models import AssociationUserTags, TagUser


class TagUserFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации тэгов пользователей.

    Поля:
        name: Имя тега.
        company_id: Идентификатор компании, в которой будет использоваться тэг.
    """

    name: str = factory.LazyAttributeSequence(lambda o, n: 'Тэг %d%d' % (o.company_id, n))
    company_id: int

    class Meta:
        model = TagUser
        sqlalchemy_session = sc_session


class AssociationUserTagsFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации данных ассоциативной модели AssociationUserTags.

    Поля:
        left_id: Идентификатор пользователя.
        right_id: Идентификатор тэга.
    """

    id: int = factory.Sequence(lambda n: n + 1)
    left_id: UUID
    right_id: int

    class Meta:
        model = AssociationUserTags
        sqlalchemy_session = sc_session


async def create_tags(count: int = FAKER_USER_TAGS_COUNT, **kwargs) -> None:
    """
    Функция для пакетного создания тэгов.

    Функция создает компанию, пользователя и указанное количество тэгов.

    Можно передать следуюшие аргументы:
        count: Количество тэгов для создания.
        company_id: Идентификатор компании для которой необходимо создать тэги.
        user_id: Идентификатор пользователя к которому нужно привязать созданные тэги.
    """
    if 'company_id' not in kwargs:
        company = next(iter(await create_companies(1)), None)
        kwargs['company_id'] = company.id
    tags = await TagUserFactory.create_batch(count, company_id=kwargs['company_id'])
    cprint(
        f'Создано {count} тэгов для компании c id: {kwargs["company_id"]}',
        'green',
    )
    if 'user_id' not in kwargs:
        user = next(
            iter(await create_company_users(count=1, company_id=kwargs['company_id'])), None
        )
        kwargs['user_id'] = user.id
    await create_user_tag_associations(user_id=kwargs['user_id'], tag_ids=[tag.id for tag in tags])


async def create_user_tag_associations(user_id: UUID, tag_ids: list[int]) -> None:
    """
    Функция для привязки тегов к пользователю.

    Поля:
        - user_id: uuid пользователя Tabit;
        - tags_ids: список идентификаторов тэгов.
    """
    for tag_id in tag_ids:
        association_user_tags_last_id = await sc_session.execute(
            select(func.max(AssociationUserTags.id))
        )
        sequence = association_user_tags_last_id.scalar() or 0
        await AssociationUserTagsFactory(left_id=user_id, right_id=tag_id, __sequence=sequence)
    cprint(
        f'Создано {len(tag_ids)} ассоциативных связей тэг-пользователь '
        f'от пользователя с id: {user_id}',
        'green',
    )


if __name__ == '__main__':
    asyncio.run(create_tags())
