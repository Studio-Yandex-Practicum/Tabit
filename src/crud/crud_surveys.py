from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config.logging import logger
from src.core.constants import TextError
from src.crud.crud_base import CRUDBase
from src.models.survey import SurveyAnswer, SurveyData, SurveySchedule, SurveyScheduleCycle
from src.schemas.survey import (
    SurveyAnswerCreate,
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
            )
            session.add(schedule)
            await session.flush()

            try:
                for cycle_data in schedule_in.cycles:
                    cycle = SurveyScheduleCycle(
                        cycle_number=cycle_data.cycle_number,
                        date_start=cycle_data.date_start,
                        survey_schedule_id=schedule.id,
                    )
                    session.add(cycle)

                await session.commit()
                await session.refresh(schedule)
                return schedule

            except Exception as cycle_error:
                await session.rollback()
                raise cycle_error

        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_CREATE_LOG} {self.model.__name__}: {error}')
            raise error

    async def get_shedule(
        self,
        session: AsyncSession,
        obj_id: int,
        obj_slug: str,
        raise_404: bool = False,
        message: str | None = None,
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
            if message is None:
                message = TextError.NOT_FOUND_BY_SLUG.format(
                    obj=self.model.__name__, slug=obj_slug
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj_model

    async def get_all_shedules(
        self,
        session: AsyncSession,
        obj_slug: str,
        raise_404: bool = False,
        message: str | None = None,
    ):
        """
        Возвращает список всех расписаний.
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.company_slug == obj_slug)
            .options(selectinload(self.model.cycles))
        )
        obj_model = result.scalars().all()
        if not obj_model and raise_404:
            if message is None:
                message = TextError.NOT_FOUND_BY_SLUG.format(
                    obj=self.model.__name__, slug=obj_slug
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
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

        if obj_in.cycles is not None:
            new_cycles = {cycle.cycle_number: cycle for cycle in obj_in.cycles}

            cycles_to_remove = []
            for existing_cycle in db_obj.cycles:
                if existing_cycle.cycle_number in new_cycles:
                    setattr(
                        existing_cycle,
                        'date_start',
                        new_cycles[existing_cycle.cycle_number].date_start,
                    )
                else:
                    cycles_to_remove.append(existing_cycle)

            for cycle in cycles_to_remove:
                db_obj.cycles.remove(cycle)

            existing_numbers = {cycle.cycle_number for cycle in db_obj.cycles}
            for cycle_number, new_cycle in new_cycles.items():
                if cycle_number not in existing_numbers:
                    db_obj.cycles.append(
                        SurveyScheduleCycle(
                            cycle_number=new_cycle.cycle_number,
                            date_start=new_cycle.date_start,
                            survey_schedule_id=db_obj.id,
                        )
                    )

        try:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
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
            survey_shedule_id=data.survey_shedule_id,
            cycle_id=data.cycle_id,
            user_id=user_id,
            company_slug=company_slug,
        )
        try:
            session.add(survey_data)
            await session.commit()
            await session.refresh(survey_data)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
            raise error
        return survey_data

    async def create_survay_answers(
        self,
        session: AsyncSession,
        survey_data_id: SurveyData,
        item: SurveyAnswerCreate,
        result: dict,
    ):
        """
        Записывает ответы и результаты теста.
        """

        answer = SurveyAnswer(
            survey_data_id=survey_data_id,
            survey_list_id=item.survey_list_id,
            answer=item.answers,
            result=result,
        )
        try:
            session.add(answer)
            await session.commit()
            await session.refresh(answer)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
            raise error
        return answer

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
