from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.crud_base import CRUDBase
from src.problems.crud.association_utils import create_associations
from src.models import AssociationUserMeeting, Meeting
from src.schemas import MeetingCreateSchema


# TODO Если участники встречи переносятся сюда автоматом из проблемы, то поправить этот метод
class CRUDMeeting(CRUDBase):
    """CRUD операции для модели встречи."""

    async def create_with_members(
        self, session: AsyncSession, meeting_data: dict, members: list[UUID]
    ) -> Meeting:
        """Создание встречи с участниками.

        Назначение:
            Создает новую встречу и добавляет участников через ассоциативную таблицу.
            Выполняет все операции в рамках одной транзакции.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            meeting_data: Словарь с данными для создания встречи.
            members: Список UUID участников встречи.
        Возвращаемое значение:
            Созданный объект встречи с обновленными данными.
        """
        try:
            meeting_data['members'] = members
            meeting_model = MeetingCreateSchema(**meeting_data)
            created_meeting = await self.create(session, meeting_model)

            # Создаем ассоциации участников с встречей
            await create_associations(
                session=session,
                association_model=AssociationUserMeeting,
                left_ids=members,
                right_id=created_meeting.id,
            )

            await session.commit()
            await session.refresh(created_meeting)
            return created_meeting

        except Exception as e:
            await session.rollback()
            raise e

    async def update_meeting(
        self, session: AsyncSession, meeting_id: int, meeting_update: dict
    ) -> Meeting:
        """Обновление встречи.

        Назначение:
            Обновляет данные встречи в базе данных по её ID.
            Перед обновлением проверяет существование встречи.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            meeting_id: ID встречи для обновления.
            meeting_update: Словарь с данными для обновления встречи.
        Возвращаемое значение:
            Обновленный объект встречи.
        """
        db_obj = await self.get_or_404(session, meeting_id)
        return await self.update(session, db_obj, meeting_update)

    async def delete_meeting(self, session: AsyncSession, meeting_id: int) -> None:
        """Удаление встречи.

        Назначение:
            Удаляет встречу из базы данных по её ID.
            Перед удалением проверяет существование встречи.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            meeting_id: ID встречи для удаления.
        Возвращаемое значение:
            None
        """
        db_obj = await self.get_or_404(session, meeting_id)
        await self.remove(session, db_obj)


meeting_crud = CRUDMeeting(Meeting)
