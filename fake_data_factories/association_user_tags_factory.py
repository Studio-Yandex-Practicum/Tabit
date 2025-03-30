from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import ColorCPrint
from fake_data_factories.utils import start_and_end
from src.database.sc_db_session import sc_session
from src.users.models import AssociationUserTags


class AssociationUserTagsFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации данных ассоциативной модели AssociationUserTags.

    Поля:
        left_id: Идентификатор пользователя.
        right_id: Идентификатор тэга.
    """

    left_id: UUID
    right_id: int

    class Meta:
        model = AssociationUserTags
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_user_tag_associations(user_id: UUID, tag_ids: list[int]) -> None:
    """
    Функция для привязки тегов к пользователю.

    Поля:
        - user_id: uuid пользователя Tabit;
        - tags_ids: список идентификаторов тэгов.
    """
    for tag_id in tag_ids:
        await AssociationUserTagsFactory(left_id=user_id, right_id=tag_id)
    cprint(
        f'Создано {len(tag_ids)} ассоциативных связей тэг-пользователь '
        f'от пользователя с id: {user_id}',
        ColorCPrint.green,  # type: ignore
    )
