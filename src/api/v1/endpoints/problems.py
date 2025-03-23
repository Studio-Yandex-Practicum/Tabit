from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.api.v1.validator import validate_owner_object, validate_user_from_company, validate_close_problem

router = APIRouter()


@router.get(
    '/{company_slug}/problems',
    response_model=list[ProblemResponseSchema],
    response_model_exclude_unset=True,
    summary='Получить список всех проблем',
    status_code=status.HTTP_200_OK,
)
async def get_problems_for_user(
    company_slug: str,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех проблем.

    Назначение:
        Возвращает список всех проблем для указанной компании.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Список объектов ProblemResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    return await problem_crud.get_multi(
        session,
        filters={'company_id': company.id},
        unique_filter_rows=True,
    )


@router.post(
    '/{company_slug}/problems',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Создать новую проблему',
    status_code=status.HTTP_201_CREATED,
)
async def create_problem(
    problem_in: ProblemCreateSchema,
    company_slug: str,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Создание проблемы.

    Назначение:
        Создает новую проблему для указанной компании.
    Параметры:
        problem: Данные для создания проблемы.
        company_slug: Уникальный идентификатор компании.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Созданный объект ProblemResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    await validate_field_members(session, problem_in.members)
    return await problem_crud.create_problem_with_members(
        session=session, problem_in=problem_in, owner=user, company=company,
    )


@router.get(
    '/{company_slug}/problems/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Получить информацию о проблеме',
    status_code=status.HTTP_200_OK,
)
async def get_problem(
    problem_id: int,
    company_slug: str,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о проблеме по ID.

    Назначение:
        Возвращает информацию о конкретной проблеме по её ID.
    Параметры:
        problem_id: ID проблемы.
        company_slug: Уникальный идентификатор компании.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект ProblemResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    return await problem_crud.get_or_404(session, problem_id)


@router.patch(
    '/{company_slug}/problems/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Обновить информацию о проблеме',
    status_code=status.HTTP_200_OK,
)
async def update_problem(
    problem_in: ProblemUpdateSchema,
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление проблемы.

    Назначение:
        Обновляет информацию о существующей проблеме.
    Параметры:
        problem: Данные для обновления проблемы.
        company_slug: Уникальный идентификатор компании.
        problem_id: ID проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Обновленный объект ProblemResponseSchema.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_owner_object(user, problem)
    validate_close_problem(problem)
    await validate_field_members(session, problem_in.members, company_id=company.id)
    return await problem_crud.update_problem(session, problem, problem_in)


@router.delete(
    '/{company_slug}/problems/{problem_id}',
    summary='Удалить проблему',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_problem(
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление проблемы.

    Назначение:
        Удаляет проблему по её ID.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: ID проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        None
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_owner_object(user, problem)
    validate_close_problem(problem)
    await problem_crud.remove(session, problem)


# TODO: На эту ручку не писались тесты.
@router.post(
    '/{company_slug}/problems/{problem_id}/confirm',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Стать участником решения проблемы',
    status_code=status.HTTP_200_OK,
)
async def confirm_participation_in_problem(
    company_slug: str,
    problem_id: int,
    user: UserTabit = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
):
    """Подтвердить участие в решение проблемы.

    Назначение:
        Удаляет проблему по её ID.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: ID проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        None
    """
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    problem = await problem_crud.get_or_404(session, problem_id)
    validate_close_problem(problem)
    await check_max_number_problems(session, user)
    return await problem_crud.edit_status_field_associations(session, problem, user)
