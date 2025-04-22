from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session
from src.schemas.survey import (
    SurveyScheduleCreate,
    SurveyScheduleRead,
    SurveyDataCreate,
    SurveyDataRead,
    SurveyScheduleCycleRead,
)
from src.crud.crud_company import company_crud
from src.crud.crud_surveys import surveys_schedule_crud, surveys_data_crud
from src.features_v1.validators import validator_check_object_exists
from src.utils.surveys import Surveys

router = APIRouter()


@router.get(
    '/',
    response_model=List[SurveyScheduleRead],
    summary='Получить список всех опросов компании',
    dependencies=[Depends(get_async_session)],
)
async def get_surveys(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Получает список всех опросов компании."""
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )

    schedule = await surveys_schedule_crud.get_by_slug(
        session=session,
        obj_slug=company_slug,
        raise_404=True,
    )
    return schedule


@router.post(
    '/',
    response_model=SurveyScheduleRead,
    summary='Создать новое расписание опросов',
    dependencies=[Depends(get_async_session)],
)
async def create_survey_schedule(
    company_slug: str,
    data: SurveyScheduleCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создает новое расписание.

    Поля:
        date_start: заполняется в формате "2019-08-24".
        status: in_progress - "В работе"
                complited - "Завершен"
                canceled - "Отменен"
                postponed - "Отложен"
        survey_tag: emo = "Определение эмоционального состояния"
                    test = "Тестовый тест для тестирования"
    """
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )

    schedule = await surveys_schedule_crud.create_surveys_schedule(
        session=session, slug=company_slug, schedule_in=data
    )
    return schedule


@router.delete(
    '/{schedule_id:int}',
    response_model=SurveyScheduleRead,
    summary='Удалить расписание опросов',
    dependencies=[Depends(get_async_session)],
)
async def delete_survey_schedule(
    company_slug: str,
    schedule_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет расписание расписание.
    """
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )

    schedule = await validator_check_object_exists(
        session=session, model_crud=surveys_schedule_crud, object_id=schedule_id
    )
    await surveys_schedule_crud.remove(session=session, db_object=schedule)
    return schedule


@router.get(
    '/{schedule_id:int}/cycles',
    response_model=List[SurveyScheduleCycleRead],
    summary='Получить список циклов опросов внутри расписания компании',
    dependencies=[Depends(get_async_session)],
)
async def get_surveys_cycles(
    company_slug: str, schedule_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Получает список циклов опросов внутри расписания компании."""
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )

    cycles = await surveys_schedule_crud.get_cycles(session=session, obj_id=schedule_id)
    return cycles


@router.get(
    '/{user_id:uuid}',
    response_model=List[SurveyDataRead],
    summary='Получить историю опросов сотрудника компании',
    dependencies=[Depends(get_async_session)],
)
async def get_employee_survey_history(
    company_slug: str,
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает историю опросов сотрудника компании."""
    # TODO: Проверить существование сотрудника
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )

    survey_data = await surveys_data_crud.get_all_user_survey(
        session=session, company_slug=company_slug, user_id=user_id
    )
    return survey_data


@router.get(
    '/{user_id}/{survey_id}',
    response_model=SurveyDataRead,
    summary='Получить информацию об опросе сотрудника компании',
    dependencies=[Depends(get_async_session)],
)
async def get_employee_survey_info(
    company_slug: str,
    user_id: UUID,
    survey_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию об опросе сотрудника компании."""
    # TODO: Проверить существование сотрудника
    # TODO: Проверить существование пройденого теста
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )

    survey_data = await surveys_data_crud.get_user_survey(
        session=session, company_slug=company_slug, survey_data_id=survey_id, user_id=user_id
    )

    return survey_data


@router.post(
    '/{uuid}',
    summary='Передать информацию об опросе сотрудника компании',
    dependencies=[Depends(get_async_session)],
)
async def add_employee_survey_info(
    company_slug: str,
    uuid: UUID,
    data: SurveyDataCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Передает информацию об опросе сотрудника компании."""
    # TODO: Проверить существование сотрудника
    # TODO: Проверить сущестрование номера теста
    await validator_check_object_exists(
        session=session, model_crud=company_crud, object_slug=company_slug
    )
    survey_data = await surveys_data_crud.create_survey_data(
        session=session, data=data, user_id=uuid, company_slug=company_slug
    )

    survey_data_id = survey_data.id

    for item in data.answers:
        result = Surveys(item=item).survey_type()
        await surveys_data_crud.create_survay_answers(
            session=session, survey_data_id=survey_data_id, item=item, result=result
        )

    return survey_data
