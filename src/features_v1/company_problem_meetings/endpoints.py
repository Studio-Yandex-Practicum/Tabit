from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_user_tabit
from src.core.database.db_depends import get_async_session
from src.crud import company_crud, meeting_crud, problem_crud, result_meeting_crud
from src.features_v1.constants import DescriptionConstants, SummaryConstants
from src.features_v1.validators import (
    check_meeting_exists,
    check_problem_exists,
    check_result_meeting_unique,
    validate_close_problem,
    validate_field_members,
    validate_is_member_problem,
    validate_meeting_was_held,
    validate_owner_object,
    validate_user_from_company,
)
from src.models import CompanyUser
from src.schemas import (
    MeetingCreateSchema,
    MeetingResponseSchema,
    MeetingResultCreateSchema,
    MeetingResultResponseSchema,
    MeetingResultUpdateSchema,
    MeetingUpdateSchema,
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[MeetingResponseSchema],
    response_model_exclude_none=True,
    summary=SummaryConstants.LIST_MEETING,
    description=DescriptionConstants.LIST_MEETING,
    status_code=status.HTTP_200_OK,
)
async def get_meetings_for_user(
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> list[MeetingResponseSchema]:
    """Получает список всех встреч.

    Назначение:
        Возвращает список всех встреч для указанной проблемы.
    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Список объектов MeetingResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    return await meeting_crud.get_multi(
        session,
        filters={'problem_id': problem_id},
        unique_filter_rows=True,
    )


@router.post(
    '/',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary=SummaryConstants.CREATE_MEETING,
    description=DescriptionConstants.CREATE_MEETING,
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting(
    meeting_in: MeetingCreateSchema,
    company_slug: str,
    problem_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> MeetingUpdateSchema:
    """Создает встречу.

    Назначение:
        Создает новую встречу для указанной проблемы.
    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        meeting_in: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект MeetingResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - участник ли пользователь в данной проблеме;
        - проверит, что переданные UUID в поле members корректны
          и принадлежат сотрудникам данной компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    validate_is_member_problem(user, problem)
    return await meeting_crud.create_with_members(session, meeting_in, user, problem)


@router.get(
    '/{meeting_id}',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary=SummaryConstants.GET_MEETING,
    description=DescriptionConstants.GET_MEETING,
    status_code=status.HTTP_200_OK,
)
async def get_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> MeetingUpdateSchema:
    """Получает информацию о встрече.

    Назначение:
        Возвращает информацию о конкретной встрече.
    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        meeting_id: идентификатор встречи, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект MeetingResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    return await meeting_crud.get_or_404(session, meeting_id)


@router.patch(
    '/{meeting_id}',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary=SummaryConstants.UPDATE_MEETING,
    description=DescriptionConstants.UPDATE_MEETING,
    status_code=status.HTTP_200_OK,
)
async def update_meeting(
    meeting_in: MeetingUpdateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> MeetingUpdateSchema:
    """Обновляет информацию о встрече.

    Назначение:
        Обновляет данные конкретной встречи.
    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        response_model_exclude_none: позволяет исключить из ответа неустановленные значения.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        meeting_in: данные в виде схемы, для создания новой записи в БД.
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        meeting_id: идентификатор встречи, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        Объект MeetingResponseSchema.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - не решена ли эта проблема;
        - существует ли встреча с данным id;
        - является ли пользователь автором данной встречи;
        - не проведена ли уже встреча;
        - проверит, что переданные UUID в поле members корректны
          и принадлежат сотрудникам данной компании.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    meeting = await meeting_crud.get_or_404(session, meeting_id)
    validate_owner_object(user, meeting)
    validate_meeting_was_held(meeting)
    await validate_field_members(session, meeting_in.members, company_id=company.id)
    return await meeting_crud.update_meeting(session, meeting, meeting_in)


@router.delete(
    '/{meeting_id}',
    summary=SummaryConstants.DELETE_MEETING,
    description=DescriptionConstants.DELETE_MEETING,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет встречу.

    Назначение:
        Удаляет конкретную встречу.
    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
        status_code: статус ответа.
    Параметры функции:
        company_slug: слаг компании, полученный из пути.
        problem_id: идентификатор проблемы, полученный из пути.
        meeting_id: идентификатор встречи, полученный из пути.
        user: получение пользователя через зависимости.
        session: асинхронная сессия через зависимость.
    Возвращаемое значение:
        None.

    Проверки:
        - существует ли компания с таким slug;
        - пользователь, сделавший запрос, из этой компании;
        - существует ли проблема с данным id;
        - существует ли встреча с данным id;
        - является ли пользователь автором данной встречи;
        - не проведена ли уже встреча.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    meeting = await meeting_crud.get_or_404(session, meeting_id)
    validate_owner_object(user, meeting)
    validate_meeting_was_held(meeting)
    await meeting_crud.remove(session, meeting)


@router.post(
    '/{meeting_id}/result',
    response_model=MeetingResultResponseSchema,
    response_model_exclude_none=True,
    summary=SummaryConstants.CREATE_RESULT_MEETING,
    description=DescriptionConstants.CREATE_RESULT_MEETING,
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting_result(
    result: MeetingResultCreateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
    owner: CompanyUser = Depends(current_user_tabit),
) -> MeetingResultResponseSchema:
    """Создает результат встречи.

    Назначение:
        Создает результат конкретной встречи.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
        owner: Текущий пользователь.
    Возвращаемое значение:
        Объект MeetingResultResponseSchema.
    """

    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(owner, company)
    await check_problem_exists(problem_id, session)
    await check_meeting_exists(meeting_id, session)
    await check_result_meeting_unique(meeting_id, owner, session)
    return await result_meeting_crud.create(session, result, owner, meeting_id)


@router.get(
    '/{meeting_id}/result/{result_id}',
    response_model=MeetingResultResponseSchema,
    response_model_exclude_none=True,
    summary=SummaryConstants.GET_RESULT_MEETING,
    description=DescriptionConstants.GET_RESULT_MEETING,
    status_code=status.HTTP_200_OK,
)
async def get_meeting_result(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    result_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> MeetingResultResponseSchema:
    """Возвращает результат встречи.

    Назначение:
        Возвращает результат конкретной встречи.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
        owner: Текущий пользователь.
    Возвращаемое значение:
        Объект MeetingResultResponseSchema.
    """

    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await check_problem_exists(problem_id, session)
    await check_meeting_exists(meeting_id, session)
    return await result_meeting_crud.get_or_404(session, result_id)


@router.patch(
    '/{meeting_id}/result/{result_id}',
    response_model=MeetingResultResponseSchema,
    response_model_exclude_none=True,
    summary=SummaryConstants.UPDATE_RESULT_MEETING,
    description=DescriptionConstants.UPDATE_RESULT_MEETING,
    status_code=status.HTTP_200_OK,
)
async def patch_meeting_result(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    result_id: int,
    result_update: MeetingResultUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    owner: CompanyUser = Depends(current_user_tabit),
) -> MeetingResultResponseSchema:
    """Обновляет результат встречи.

    Назначение:
        Обновляет результат конкретной встречи.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
        owner: Текущий пользователь.
    Возвращаемое значение:
        Объект MeetingResultResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(owner, company)
    await check_problem_exists(problem_id, session)
    await check_meeting_exists(meeting_id, session)
    result_data = await result_meeting_crud.get_or_404(session, result_id)
    return await result_meeting_crud.update(session, result_data, result_update)
