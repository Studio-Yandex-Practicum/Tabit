from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.core.config.logging import logger
from src.crud import CRUDBase
from src.crud.constants import TextErrorConstants
from src.models import (
    CompanyUser,
    MeetingResult,
)


class CRUDMeetingResult(CRUDBase):
    """CRUD операции для модели результата встречи."""

    async def get(self, session: AsyncSession, obj_id: int) -> MeetingResult | None:
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
        owner: CompanyUser,
        meeting_id: int,
    ) -> MeetingResult:
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
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj


result_meeting_crud = CRUDMeetingResult(MeetingResult)
