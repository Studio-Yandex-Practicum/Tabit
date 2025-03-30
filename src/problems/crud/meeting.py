from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.constants import ZERO, TextError
from src.crud import CRUDBase, CRUDBaseWithAssociations
from src.logger import logger
from src.problems.models import AssociationUserMeeting, Meeting, Problem, ResultMeeting
from src.problems.models.enums import StatusMeeting, StatusProblem
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingUpdateSchema,
)
from src.users.models import UserTabit


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


class CRUDResultMeeting(CRUDBase):
    """CRUD операции для модели результата встречи."""

    async def get(self, session: AsyncSession, obj_id: int) -> ResultMeeting | None:
        """Возвращает результат встречи по ID.

        Назначение:
            Извлекает результать встречи из базы данных по ID,
            используя стратегию жадной загрузки (joinedload)
            связанных данных через SQL-запрос с JOIN.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            filters: Ключевые аргументы, представляющие поля модели Meeting
            и их значения для фильтрации.
        Возвращаемое значение:
            Объект результата встречи, если такой объект существует, иначе None.
        """
        result = await session.execute(
            select(self.model)
            .options(joinedload(self.model.meeting))
            .where(self.model.id == obj_id)
        )
        return result.scalars().first()

    async def create(
        self,
        session: AsyncSession,
        obj_in: dict,
        owner: UserTabit,
        meeting_id: int,
    ) -> ResultMeeting:
        """Создает результат встречи.

        Назначение:
            Создает новый результат встречи.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            obj_in: Словарь с данными для создания результата встречи.
            owner: Текущий пользователь.
            meeting_id: ID встречи.
        Возвращаемое значение:
            Созданный объект результата встречи.
        """
        obj_data = obj_in.model_dump()
        obj_data['owner_id'] = owner.id
        obj_data['meeting_id'] = meeting_id
        db_obj = self.model(**obj_data)
        try:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_CREATE_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj


result_meeting_crud = CRUDResultMeeting(ResultMeeting)
