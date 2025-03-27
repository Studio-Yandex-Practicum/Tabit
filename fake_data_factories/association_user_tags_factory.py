from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy import func, select
from termcolor import cprint

from src.database.sc_db_session import sc_session
from src.users.models import AssociationUserTags


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
