from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session
from src.problems.crud.problems import problem_crud
from src.schemas import (
    ProblemCreateSchema,
    ProblemResponseSchema,
    ProblemUpdateSchema,
)

router = APIRouter()


@router.get(
    '/{company_slug}/problems',
    response_model=List[ProblemResponseSchema],
    response_model_exclude_unset=True,
    summary='Получить список всех проблем',
    status_code=status.HTTP_200_OK,
)
async def get_all_problems(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """Получает список всех проблем.

    Назначение:
        Возвращает список всех проблем для указанной компании.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Список объектов ProblemResponseSchema.
    """
    filters = {'company_slug': company_slug}
    return await problem_crud.get_multi(session, filters=filters)


@router.post(
    '/{company_slug}/problems',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Создать новую проблему',
    status_code=status.HTTP_201_CREATED,
)
async def create_problem(
    problem: ProblemCreateSchema,
    company_slug: str,
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
    problem_data = problem.model_dump()
    members = problem.members or []
    created_problem = await problem_crud.create_with_members(
        session=session, problem_data=problem_data, members=members
    )
    return created_problem


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
    return await problem_crud.get_or_404(session, problem_id)


@router.patch(
    '/{company_slug}/problems/{problem_id}',
    response_model=ProblemResponseSchema,
    response_model_exclude_unset=True,
    summary='Обновить информацию о проблеме',
    status_code=status.HTTP_200_OK,
)
async def update_problem(
    problem: ProblemUpdateSchema,
    company_slug: str,
    problem_id: int,
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
    return await problem_crud.update_problem(session, problem_id, problem)


@router.delete(
    '/{company_slug}/problems/{problem_id}',
    summary='Удалить проблему',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_problem(
    company_slug: str,
    problem_id: int,
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
    await problem_crud.delete_problem(session, problem_id)
