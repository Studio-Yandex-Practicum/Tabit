from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud.constants import TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models.survey import (
    SurveyData,
    SurveySchedule,
)
from src.schemas.survey import (
    SurveyDataCreate,
    SurveyScheduleCreate,
    SurveyScheduleUpdate,
)


class CRUDSurveysSchedule(CRUDBase):
    """
    CRUD операции для модели тестирований.
    """

    async def create_surveys_schedule(
        self,
        session: AsyncSession,
        slug: str,
        schedule_in: SurveyScheduleCreate,
    ):
        """
        Создает новое расписание.
        """

        try:
            schedule = self.model(
                survey_tag=schedule_in.survey_tag,
                company_slug=slug,
                status=schedule_in.status,
                cycles_dates=[d.isoformat() for d in schedule_in.cycles_dates]
            )
            session.add(schedule)
            await session.commit()
            await session.refresh(schedule)
            return schedule
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

    async def get_shedule(
        self,
        session: AsyncSession,
        obj_id: int,
        obj_slug: str,
        raise_404: bool = False,
    ):
        """
        Возвращает расписание.
        """
        result = await session.execute(
            select(self.model).where(
                (self.model.company_slug == obj_slug) & (self.model.id == obj_id)
            )
        )
        obj_model = result.scalars().first()
        if not obj_model and raise_404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Расписание не найдено'
            )
        return obj_model

    async def get_all_shedules(
        self,
        session: AsyncSession,
        obj_slug: str
    ):
        """
        Возвращает список всех расписаний.
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.company_slug == obj_slug)
        )
        obj_model = result.scalars().all()
        return obj_model

    async def update_shedule(
        self, session: AsyncSession, db_obj: SurveySchedule, obj_in: SurveyScheduleUpdate
    ):
        """
        Обновляет расписание.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in ['survey_tag', 'status']:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        if obj_in.cycles_dates is not None:
            cycles = [d.isoformat() for d in obj_in.cycles_dates]
            setattr(db_obj, 'cycles_dates', cycles)

        try:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.UPDATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj


class CRUDSurveysData(CRUDBase):
    """
    CRUD операции для работы с данными прохождения тестирования.
    """

    async def create_survey_data(
        self, session: AsyncSession, data: SurveyDataCreate, user_id: UUID, company_slug: str
    ):
        """
        Создает запись о прохождении теста в цикле.
        """

        survey_data = self.model(
            shedule_id=data.shedule_id,
            cycle_date=data.cycle_date,
            user_id=user_id,
            company_slug=company_slug,
            results=data.results,
            answers=[a.model_dump() for a in data.answers]
        )
        session.add(survey_data)
        await session.commit()
        await session.refresh(survey_data)
        return survey_data

    async def get_user_survey(
        self, session: AsyncSession, company_slug: str, survey_data_id: int, user_id: UUID
    ):
        """
        Получает информацию об опросе пользователя.
        """

        result = await session.execute(
            select(self.model).where(
                self.model.id == survey_data_id
                and self.model.user_id == user_id
                and self.model.company_slug == company_slug
            )
        )
        return result.scalars().first()

    async def get_all_user_survey(self, session: AsyncSession, company_slug: str, user_id: UUID):
        """
        Получает информацию обо всех опросах пользователя.
        """

        result = await session.execute(
            select(self.model).where(
                (self.model.user_id == user_id) & (self.model.company_slug == company_slug)
            )
        )
        return result.scalars().all()


surveys_data_crud = CRUDSurveysData(SurveyData)
surveys_schedule_crud = CRUDSurveysSchedule(SurveySchedule)
