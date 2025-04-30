from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.core.database.db_depends import get_async_session
from src.crud import surveys_data_crud, surveys_list_crud, surveys_schedule_crud, user_crud
from src.crud.constants import TextError
from src.features_v1.validators import (
    check_company_exists,
    validate_employee_survey_history,
    validate_user_from_company,
    validator_check_object_exists,
)
from src.schemas.survey import (
    SurveyDataCreate,
    SurveyDataRead,
    SurveyScheduleCreate,
    SurveyScheduleRead,
    SurveyScheduleUpdate,
)
from src.utils.surveys import Surveys

router = APIRouter()


@router.get(
    '/',
    response_model=List[SurveyScheduleRead],
    summary='Получить список всех опросов компании',
    description='Получить список всех опросов компании.'
    'Права доступа: Tabit Admin, Tabit Superuser.',
    status_code=status.HTTP_200_OK,
)
async def get_schedule_list(
    company_slug: str, session: AsyncSession = Depends(get_async_session)
) -> List[SurveyScheduleRead]:
    """
    Возвращает список всех опросов компании.

    Назначение:
        Для получения списка всех расписаний проводившихся опросов.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Список объектов SurveyScheduleRead.

    Проверки:
        - существует ли компания с таким slug;
        - существуют ли расписания у данной компании.
    """
    await check_company_exists(session=session, company_slug=company_slug)

    schedule = await surveys_schedule_crud.get_all_shedules(
        session=session,
        obj_slug=company_slug,
        raise_404=False,
    )
    return schedule


@router.post(
    '/',
    response_model=SurveyScheduleRead,
    summary='Создать новое расписание опросов',
    description='Создать новое расписание опросов. '
    'Права доступа: Tabit Admin, Tabit Superuser.',
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
    company_slug: str,
    data: SurveyScheduleCreate,
    session: AsyncSession = Depends(get_async_session),
) -> SurveyScheduleRead:
    """
    Создает новое расписание.

    Назначение:
        Создает новое расписание..
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        data: данные в виде схемы, для создания новой записи в БД.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект SurveyScheduleRead.

    Проверки:
        - существует ли компания с таким slug
    """
    await check_company_exists(session=session, company_slug=company_slug)

    schedule = await surveys_schedule_crud.create_surveys_schedule(
        session=session, slug=company_slug, schedule_in=data
    )
    return schedule


@router.get(
    '/{schedule_id:int}',
    response_model=SurveyScheduleRead,
    summary='Получить конкретное расписание опросов компании',
    description='Получить конкретное расписание опросов компании.'
    'Права доступа: Tabit Admin, Tabit Superuser.',
    status_code=status.HTTP_200_OK,
)
async def get_schedule(
    company_slug: str, schedule_id: int, session: AsyncSession = Depends(get_async_session)
) -> SurveyScheduleRead:
    """
    Возвращает конкретное расписание опросов компании.

    Назначение:
        Для получения расписания опросов.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        schedule_id: идентификатор расписания, полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект SurveyScheduleRead.

    Проверки:
        - существует ли компания с таким slug;
        - существует ли расписание с данным id.
    """
    await check_company_exists(session=session, company_slug=company_slug)

    schedule = await surveys_schedule_crud.get_shedule(
        session=session,
        obj_id=schedule_id,
        obj_slug=company_slug,
        raise_404=True,
    )
    return schedule


@router.patch(
    '/{schedule_id:int}',
    response_model=SurveyScheduleRead,
    summary='Изменить расписание опросов',
    description='Внести изменение в расписание опросов. '
    'Права доступа: Tabit Admin, Tabit Superuser.',
    status_code=status.HTTP_200_OK,
)
async def update_survey_schedule(
    company_slug: str,
    schedule_id: int,
    data: SurveyScheduleUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> SurveyScheduleRead:
    """
    Вносит изменения в новое расписание.

    Назначение:
        Для изменения значений в расписании.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        data: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        schedule_id: идентификатор расписания, полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект SurveyScheduleRead.

    Проверки:
        - существует ли компания с таким slug;
        - существует ли расписание с данным id;
    """
    await check_company_exists(session=session, company_slug=company_slug)
    schedule = await surveys_schedule_crud.get_shedule(
        session=session,
        obj_id=schedule_id,
        obj_slug=company_slug,
        raise_404=True,
    )
    updated_shedule = await surveys_schedule_crud.update_shedule(
        session=session, db_obj=schedule, obj_in=data
    )

    return updated_shedule


@router.delete(
    '/{schedule_id:int}',
    summary='Удалить расписание опросов',
    description='Позволяет удалить расписание опросов.'
    ' Права доступа: Tabit Admin, Tabit Superuser',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_survey_schedule(
    company_slug: str,
    schedule_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Удаляет расписание.

    Назначение:
        Удаляет конкретное расписание.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        schedule_id: идентификатор расписания, полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        None.

    Проверки:
        - существует ли компания с таким slug;
        - существует ли расписание с данным id;
    """
    await check_company_exists(session=session, company_slug=company_slug)

    schedule = await validator_check_object_exists(
        session=session, model_crud=surveys_schedule_crud, object_id=schedule_id
    )
    await surveys_schedule_crud.remove(session=session, db_object=schedule)


@router.get(
    '/{user_id:uuid}',
    response_model=List[SurveyDataRead],
    summary='Получить историю опросов сотрудника компании',
    description='Позволяет получить испорию всех пройденых опросов'
    ' пользователя. Права доступа: Company User.',
    status_code=status.HTTP_200_OK,
)
async def get_employee_survey_history(
    company_slug: str,
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> List[SurveyDataRead]:
    """
    Получает историю опросов сотрудника компании.

    Назначение:
        Для получения истории опросов сотрудника компании.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        user_id: идентификатор пользователя полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Список объектов List[SurveyDataRead].

    Проверки:
        - существует ли компания с таким slug;
        - существует ли пользователь с таким UUID
    """

    await check_company_exists(session=session, company_slug=company_slug)
    await user_crud.get_or_404(session=session, obj_id=user_id)

    survey_data = await surveys_data_crud.get_all_user_survey(
        session=session, company_slug=company_slug, user_id=user_id
    )
    #validate_employee_survey_history(survey_data)
    return survey_data


@router.get(
    '/{user_id:uuid}/{survey_id:int}',
    response_model=SurveyDataRead,
    summary='Получить информацию об опросе сотрудника компании',
    description='Позволяет получить информацию о конкретном опросе'
    ' пользователя. Права доступа: Company User.',
    status_code=status.HTTP_200_OK,
)
async def get_employee_survey_info(
    company_slug: str,
    user_id: UUID,
    survey_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> SurveyDataRead:
    """
    Получает информацию об опросе сотрудника компании.

    Назначение:
        Для получения информации по конкретном опросе.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        survey_id: идентификатор записи о прохождении, полученный из пути.
        user_id: идентификатор пользователя полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект SurveyDataRead.

    Проверки:
        - существует ли компания с таким slug.
        - существует ли пользователь с таким UUID.
    """

    await check_company_exists(session=session, company_slug=company_slug)
    await user_crud.get_or_404(session=session, obj_id=user_id)
    await validator_check_object_exists(
        session=session, model_crud=surveys_data_crud, object_id=survey_id
    )
    survey_data = await surveys_data_crud.get_user_survey(
        session=session, company_slug=company_slug, survey_data_id=survey_id, user_id=user_id
    )

    return survey_data


@router.post(
    '/{user_id:uuid}',
    response_model=SurveyDataRead,
    summary='Передать информацию об опросе сотрудника компании',
    description='Позволяет передать данные о прохождении опроса пользователем.'
    ' Права доступа: Company User.',
    status_code=status.HTTP_201_CREATED,
)
async def add_employee_survey_info(
    company_slug: str,
    user_id: UUID,
    data: SurveyDataCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Передает информацию об опросе сотрудника компании.

    Назначение:
        Записывет данные об прохождении опроса.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        data: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        user_id: идентификатор пользователя полученный из пути.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект SurveyDataRead.

    Проверки:
        - существует ли компания с таким slug.
        - существует ли user с таким UUID.
        - есть ли разрешение у пользователя добавлять ответы в опросе этой компании.
        - существует ли расписание.
        - существует ли тест.
        - существует ли цикл в расписании.

    Все проверки и записи объединены в одну транзакцию,
    в случае ошибки на любом из этапов будет rollback.
    В случае успеха будет автоматический commit.
    """

    async with session.begin():
        try:
            company = await check_company_exists(session=session, company_slug=company_slug)
            user = await user_crud.get_or_404(session=session, obj_id=user_id)
            validate_user_from_company(user, company)
            await validator_check_object_exists(
                session=session, model_crud=surveys_schedule_crud, object_id=data.survey_shedule_id
            )
            await surveys_schedule_crud.get_cycle(
                session=session,
                cycle_id=data.cycle_id,
                shedule_id=data.survey_shedule_id,
                raise_404=True
            )
            survey_data = await surveys_data_crud.create_survey_data(
                session=session, data=data, user_id=user_id, company_slug=company_slug
            )
            survey_data_id = survey_data.id
            for item in data.answers:
                await validator_check_object_exists(
                    session=session, model_crud=surveys_list_crud, object_id=item.survey_list_id
                )

                result = Surveys(item=item).survey_type()
                await surveys_data_crud.create_survay_answers(
                    session=session, survey_data_id=survey_data_id, item=item, result=result
                )
        except SQLAlchemyError as db_error:
            logger.error(f'Ошибка базы данных при записи результатов опроса: {db_error}')
            raise HTTPException(
                status_code=500, detail="Ошибка сервера при работе с базой данных.")
        except Exception as error:
            logger.error(
                f'{TextError.UPDATE_SERVER_LOG} в бд результата опроса: {error}')
            raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")

    survey_data = await surveys_data_crud.get_user_survey(
        session=session, company_slug=company_slug, survey_data_id=survey_data_id, user_id=user_id
    )
    return survey_data
