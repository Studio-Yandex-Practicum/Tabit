from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import ColorCPrintConstants
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import AssociationUserMeeting


class AssociationUserMeetingFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных ассоциативной модели `AssociationUserMeeting`.

    Поля:
        - `left_id`: Обязательное поле. Ссылка на пользователя Tabit. \
            Должен быть создан объект `CompanyUser`, чтобы передать полю id (типа uuid).
        - `right_id`: Обязательное поле. Ссылка на встречу. \
            Должен быть создан объект `Meeting`, чтобы передать полю id.
    """

    left_id: UUID
    right_id: int

    class Meta:
        model = AssociationUserMeeting
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_user_meeting_association(
    user_id: UUID, meeting_ids: list[int]
) -> list[AssociationUserMeeting]:
    """
    Создать запись(-и) в таблицу объекта `AssociationUserMeeting`.

    Поля:
        - `user_id`: uuid пользователя Tabit;
        - `meeting_ids`: список id встреч.

    Функция возвращает список созданных записей.
    """
    user_meeting_associations = []
    for meeting_id in meeting_ids:
        user_meeting_associations.append(
            await AssociationUserMeetingFactory.create(left_id=user_id, right_id=meeting_id)
        )
    cprint(
        f'Создано {len(meeting_ids)} ассоциативных связей встреча-пользователь '
        f'от пользователя с id: {user_id}',
        ColorCPrintConstants.green,  # type: ignore
    )
    return user_meeting_associations
