from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_user_tabit
from src.core.database.db_depends import get_async_session
from src.crud import company_crud, meeting_crud, problem_crud, result_meeting_crud
from src.features_v1.constants import Description, Summary
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
from src.models import UserTabit
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
    summary=Summary.MEETING_LIST,
    description=Description.MEETING_LIST,
    status_code=status.HTTP_200_OK,
)
async def get_meetings_for_user(
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> list[MeetingResponseSchema]:
    """Получает список всех встреч.

    Назначение:
        Возвращает список всех встреч для указанной проблемы.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
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
    summary=Summary.MEETING_CREATE,
    description=Description.MEETING_CREATE,
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting(
    meeting_in: MeetingCreateSchema,
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> MeetingUpdateSchema:
    """Создает встречу.

    Назначение:
        Создает новую встречу для указанной проблемы.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
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
    summary=Summary.MEETING,
    description=Description.MEETING,
    status_code=status.HTTP_200_OK,
)
async def get_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> MeetingUpdateSchema:
    """Получает информацию о встрече.

    Назначение:
        Возвращает информацию о конкретной встрече.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
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
    summary=Summary.MEETING_UPDATE,
    description=Description.MEETING_UPDATE,
    status_code=status.HTTP_200_OK,
)
async def update_meeting(
    meeting_in: MeetingUpdateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> MeetingUpdateSchema:
    """Обновляет информацию о встрече.

    Назначение:
        Обновляет данные конкретной встречи.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
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
    summary=Summary.MEETING_DELETE,
    description=Description.MEETING_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет встречу.

    Назначение:
        Удаляет конкретную встречу.
    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
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
    summary='Создать результат встречи',
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting_result(
    result: MeetingResultCreateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
    owner: UserTabit = Depends(current_user_tabit),
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
    summary='Результат встречи',
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
    summary='Обновить результат встречи',
    status_code=status.HTTP_200_OK,
)
async def patch_meeting_result(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    result_id: int,
    result_update: MeetingResultUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    owner: UserTabit = Depends(current_user_tabit),
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
