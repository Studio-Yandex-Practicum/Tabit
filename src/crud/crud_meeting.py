from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud import CRUDBaseWithAssociations
from src.crud.constants import ZERO, TextError
from src.models import (
    AssociationUserMeeting,
    CompanyUser,
    Meeting,
    Problem,
    StatusMeeting,
    StatusProblem,
)
from src.schemas import (
    MeetingCreateSchema,
    MeetingUpdateSchema,
)


class CRUDMeeting(CRUDBaseWithAssociations):
    """CRUD операции для модели встречи."""

    async def create_with_members(
        self,
        session: AsyncSession,
        meeting_in: MeetingCreateSchema,
        owner: CompanyUser,
        problem: Problem,
    ) -> Meeting:
        """Создание встречи с участниками.

        Назначение:
            Создает новую встречу и добавляет участников через ассоциативную таблицу.
            Выполняет все операции в рамках одной транзакции.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            meeting_in: Словарь с данными для создания встречи.
            owner: экземпляр модели пользователя, автор встречи.
            problem: экземпляр модели проблемы, для решения которой организуется встреча.
        Возвращаемое значение:
            Созданный объект встречи.
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
                    )
                    for member in problem.members
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
            meeting_db: экземпляр модели встречи.
            meeting_in: данные для изменения в виде схемы.
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
                        )
                        for member in add_rows
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


meeting_crud = CRUDMeeting(Meeting, AssociationUserMeeting)
