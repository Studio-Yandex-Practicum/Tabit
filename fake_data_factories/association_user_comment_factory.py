from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import ColorCPrintConstants
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import AssociationUserComment


class AssociationUserCommentFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных ассоциативной модели AssociationUserComment.

    Поля:
        - left_id: Обязательное поле. Ссылка на пользователя Tabit.
        - right_id: Обязательное поле. Ссылка на комментарий.
    """

    left_id: UUID
    right_id: int

    class Meta:
        model = AssociationUserComment
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_user_comment_associations(
    user_id: UUID,
    comment_ids: list[int],
) -> None:
    """
    Создать записи в таблицу объекта AssociationUserComment.

    Поля:
        - user_id: uuid пользователя Tabit;
        - comment_ids: список id комментариев.
    """
    for comment_id in comment_ids:
        await AssociationUserCommentFactory(left_id=user_id, right_id=comment_id)
    cprint(
        f'Создано {len(comment_ids)} ассоциативных связей комментарий-пользователь '
        f'от пользователя с id: {user_id}',
        ColorCPrintConstants.green,  # type: ignore
    )
