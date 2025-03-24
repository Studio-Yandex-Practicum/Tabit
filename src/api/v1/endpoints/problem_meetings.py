from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_user_tabit
from src.api.v1.constants import Description, Summary
from src.api.v1.validator import (
    validate_close_problem,
    validate_is_member_problem,
    validate_meeting_was_held,
    validate_owner_object,
    validate_user_from_company,
)
from src.api.v1.validators.members import validate_field_members
from src.companies.crud import company_crud
from src.database.db_depends import get_async_session
from src.problems.crud.meeting import meeting_crud
from src.problems.crud.problems import problem_crud
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingResponseSchema,
    MeetingUpdateSchema,
)
from src.users.models import UserTabit

router = APIRouter()


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings',
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
    '/{company_slug}/problems/{problem_id}/meetings',
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
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
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
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
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
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
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
