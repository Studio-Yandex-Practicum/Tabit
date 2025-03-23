from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators.meeting_validators import (
    check_meeting_date_available,
    check_meeting_title_unique,
    check_problem_exists,
)
from src.api.v1.validators.problems_validators import check_company_exists
from src.database.db_depends import get_async_session
from src.problems.crud.meeting import meeting_crud
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingResponseSchema,
    MeetingUpdateSchema,
)
from src.api.v1.validators.problems_validators import check_company_exists, check_max_number_problems
from src.database.db_depends import get_async_session
from src.problems.crud.problems import problem_crud
from src.problems.schemas.problem import (
    ProblemCreateSchema,
    ProblemResponseSchema,
    ProblemUpdateSchema,
)
from src.api.v1.auth.dependencies import (
    current_user_tabit,
    current_admin_tabit,
    current_superuser,
    get_current_admin_refresh_token,
    get_current_admin_token,
    tabit_admin,
)
from src.users.models import UserTabit
from src.companies.crud import company_crud
from src.api.v1.validators.members import validate_field_members
from src.api.v1.validator import (
    validate_owner_object, validate_user_from_company, validate_is_member_problem,
    validate_close_problem, validate_meeting_was_held,
)


router = APIRouter()


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings',
    response_model=list[MeetingResponseSchema],
    response_model_exclude_none=True,
    summary='Получить список всех встреч',
    status_code=status.HTTP_200_OK,
)
async def get_meetings_for_user(
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех встреч.

    Назначение:
        Возвращает список всех встреч для указанной проблемы.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Список объектов MeetingResponseSchema.
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
    summary='Создать встречу',
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting(
    meeting: MeetingCreateSchema,
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Создает встречу.

    Назначение:
        Создает новую встречу для указанной проблемы.
    Параметры:
        meeting: Данные для создания встречи.
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект MeetingResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    validate_is_member_problem(user, problem)
    return await meeting_crud.create_with_members(session, meeting, user, problem)


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary='Получить информацию о встрече',
    status_code=status.HTTP_200_OK,
)
async def get_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию о встрече.

    Назначение:
        Возвращает информацию о конкретной встрече.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект MeetingResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    return await meeting_crud.get_or_404(session, meeting_id)


@router.patch(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary='Обновить информацию о встрече',
    status_code=status.HTTP_200_OK,
)
async def update_meeting(
    meeting_in: MeetingUpdateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Обновляет информацию о встрече.

    Назначение:
        Обновляет данные конкретной встречи.
    Параметры:
        meeting: Данные для обновления встречи.
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
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
    summary='Удалить встречу',
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
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        None.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await problem_crud.get_or_404(session, problem_id)
    meeting = await meeting_crud.get_or_404(session, meeting_id)
    validate_owner_object(user, meeting)
    validate_meeting_was_held(meeting)
    await meeting_crud.remove(session, meeting)
