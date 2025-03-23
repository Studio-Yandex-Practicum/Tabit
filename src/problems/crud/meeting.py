from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, Table

from src.crud import CRUDBaseWithAssociations
from src.problems.crud.association_utils import create_associations
from src.problems.models import AssociationUserMeeting, Meeting
from src.problems.schemas.meeting import MeetingCreateSchema
from src.users.models import UserTabit
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingResponseSchema,
    MeetingUpdateSchema,
)
from src.problems.models import Problem
from src.problems.models.enums import StatusMeeting, StatusProblem
from src.constants import ZERO
from src.logger import logger
from src.constants import (
    DEFAULT_AUTO_COMMIT,
    DEFAULT_LIMIT,
    DEFAULT_SKIP,
    TextError,
)
from fastapi.encoders import jsonable_encoder


class CRUDMeeting(CRUDBaseWithAssociations):
    """CRUD операции для модели встречи."""

    async def create_with_members(
        self,
        session: AsyncSession,
        meeting_in: MeetingCreateSchema,
        owner: UserTabit,
        problem: Problem,
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
        meeting_data = meeting_in.model_dump()
        default_data = {
            'problem_id': problem.id,
            'owner_id': owner.id,
            'status': StatusMeeting.NEW,
            'transfer_counter': ZERO,
        }
        meeting_data.update(default_data)
        meeting_db = self.model(**meeting_data)
        try:
            session.add(meeting_db)
            await session.flush()

            if problem.members:
                associations_data = [
                    self.associations_model(
                        left_id=member.left_id,
                        right_id=meeting_db.id,
                    ) for member in problem.members
                ]
                session.add_all(associations_data)

            if problem.status == StatusProblem.NEW:
                problem.status = StatusProblem.IN_PROGRESS
                session.add(problem)
            await session.commit()
            await session.refresh(meeting_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_CREATE_LOG} {self.model.__name__}: {error}')
            raise error
        return meeting_db

    # TODO: Следующий метод полностью повторяет метод update_problem из CRUDProblem
    # Т.к. пока не ясно, как будет меняться логика проекта, эти методы пусть нарушают DRY
    # Так легче вносить правки в отдельные круды. В последствие, если правок не будет,
    # можно добавить метод update_with_associations в CRUDBaseWithAssociations
    # Уже есть отличия - в подсчете переносе даты
    async def update_meeting(
        self,
        session: AsyncSession,
        meeting_db: Meeting,
        meeting_in: MeetingUpdateSchema,
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
        meeting_data = jsonable_encoder(meeting_db)
        meeting_update_data = meeting_in.model_dump(exclude_unset=True)
        members = meeting_update_data.pop('members') if 'members' in meeting_update_data else None

        old_data_meeting = meeting_db.date_meeting

        for field in meeting_data:
            if field in meeting_update_data:
                setattr(meeting_db, field, meeting_update_data[field])

        if old_data_meeting < meeting_db.date_meeting:
            meeting_db.transfer_counter += 1

        try:
            session.add(meeting_db)
            await session.flush()

            if members is not None:
                if meeting_db.owner_id:
                    members.append(meeting_db.owner_id)
                members = set(members)

                add_rows, delete_rows = self.get_data_associations_for_updata(
                    meeting_data['members'],
                    members,
                )

                if add_rows:
                    associations_data = [
                        self.associations_model(
                            left_id=member,
                            right_id=meeting_db.id,
                        ) for member in add_rows
                    ]
                    session.add_all(associations_data)

                await session.execute(
                    delete(self.associations_model).where(
                        self.associations_model.right_id == meeting_db.id,
                        self.associations_model.left_id.in_(delete_rows),
                    )
                )

            await session.commit()
            await session.refresh(meeting_db)

        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
            raise error

        return meeting_db

    async def get_meeting(self, session: AsyncSession, **filters):
        """Получает встречу по указанным параметрам модели.

        Назначение:
            Извлекает встречу из базы данных по указанным параметрам,
            соответствующим полям модели Meeting. Возвращает объект встречи,
            если такая встреча существует; иначе - None.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            filters: Ключевые аргументы, представляющие поля модели Meeting
            и их значения для фильтрации.
        Возвращаемое значение:
            Объект встречи, если такая встреча существует с заданными параметрами, иначе None.
        """

        query = select(Meeting)
        for key, value in filters.items():
            if hasattr(Meeting, key):
                query = query.where(getattr(Meeting, key) == value)
        result = await session.execute(query)
        return result.scalar_one_or_none() is None


meeting_crud = CRUDMeeting(Meeting, AssociationUserMeeting)
