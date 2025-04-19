from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from src.crud.crud_base import CRUDBase
from src.schemas.survey import SurveyScheduleCreate, SurveyDataCreate
from src.models.survey import (
    SurveySchedule, SurveyScheduleCycle, SurveyData)
from src.core.constants import (
    TextError,
)


class CRUDSurveysSchedule(CRUDBase):
    """CRUD операции для модели тестирований."""

    async def create_surveys_schedule(
            self,
            session: AsyncSession,
            slug:  str,
            schedule_in: SurveyScheduleCreate,
    ):
        """Создает новое расписание."""

        schedule = self.model(
            survey_tag=schedule_in.survey_tag,
            company_slug=slug,
            status=schedule_in.status,
        )
        session.add(schedule)
        await session.flush()

        for cycle_data in schedule_in.cycles:
            cycle = SurveyScheduleCycle(
                date_start=cycle_data.date,
                survey_schedule_id=schedule.id,
            )
            session.add(cycle)

        await session.commit()
        await session.refresh(schedule)
        return schedule

    async def get_by_slug(
        self,
        session: AsyncSession,
        obj_slug: str,
        raise_404: bool = False,
        message: str | None = None,
    ):
        """
        Получает объект по полю slug.

        Возвращает объект модели или None, если он не найден.
        Если параметр raise_404 = True, тогда выбрасывает 404-ошибку, если не найден.
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.company_slug == obj_slug))
        obj_model = result.scalars().all()
        if not obj_model and raise_404:
            if message is None:
                message = TextError.NOT_FOUND_BY_SLUG.format(
                    obj=self.model.__name__, slug=obj_slug
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj_model


class CRUDSurveysData(CRUDBase):
    """CRUD операции для работы с ответами."""

    async def create_survey_data(
            self,
            session: AsyncSession,
            data: SurveyDataCreate,
            user_id: UUID,
            company_slug: str
    ):
        """Записывает результаты прохождения теста"""

        for item in data.answers:
            print(item)
            survey_data = self.model(
                survey_shedule_id=data.survey_shedule_id,
                cycle_id=data.cycle_id,
                survey_list_id=item.survey_list_id,
                answers=item.answers,
                user_id=user_id,
                company_slug=company_slug
            )
            session.add(survey_data)
        await session.commit()
        return {"result"}


surveys_data_crud = CRUDSurveysData(SurveyData)
surveys_schedule_crud = CRUDSurveysSchedule(SurveySchedule)
