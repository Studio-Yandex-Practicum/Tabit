from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.constants import TextError
from src.crud import CRUDBase
from src.logger import logger
from src.problems.crud.association_utils import create_associations
from src.problems.models import AssociationUserMeeting, Meeting, ResultMeeting
from src.problems.schemas.meeting import MeetingCreateSchema
from src.users.models.models import UserTabit


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
            meeting_data.pop('members', None)
            meeting_model = MeetingCreateSchema(**meeting_data)
            created_meeting = await self.create(session, meeting_model)

            # Связываем участников
            if members:
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


meeting_crud = CRUDMeeting(Meeting)


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
