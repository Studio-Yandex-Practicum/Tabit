from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.company_problem_tasks.constants import (
    ERROR_COMPANY_NOT_FOUND,
    ERROR_PROBLEM_NOT_FOUND,
    ERROR_TASK_FOR_PROBLEM_NOT_FOUND,
    ERROR_TASK_NOT_FOUND,
)
from src.features_v1.company_problem_tasks.crud_company import company_crud
from src.features_v1.company_problem_tasks.crud_problem import problem_crud
from src.features_v1.company_problem_tasks.crud_task import task_crud


async def check_task_exists(task_id: int, session: AsyncSession):
    """Проверяет, существует ли задача в базе данных.

    Args:
        task_id: Идентификатор задачи.
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если задача не найдена.
    """
    return await task_crud.get_or_404(session, task_id, message=ERROR_TASK_NOT_FOUND)


async def check_tasks_for_company_problem_exist(
    company_slug: str, problem_id: int, session: AsyncSession
):
    """Проверяет, существуют ли задачи в базе данных.

    Args:
        company_slug: Уникальный идентификатор компании
        problem_id: Идентификатор проблемы
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если задача не найдена.
    """
    tasks = await task_crud.get_by_company_and_problem(session, company_slug, problem_id)
    if tasks is None or tasks == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_TASK_FOR_PROBLEM_NOT_FOUND,
        )


async def check_company_exists(company_slug: str, session: AsyncSession):
    """Проверяет существование компании по slug.

    Назначение:
        Валидирует, что компания существует в базе данных по заданному slug.
    Параметры:
        company_slug: Строка, представляющая slug компании для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная компания, если она существует.
    Исключения:
        HTTPException: Если компания не найдена.
    """

    if not await company_crud.get_by_company_slug(session, company_slug):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_COMPANY_NOT_FOUND)


async def check_problem_exists(problem_id: int, session: AsyncSession):
    """Проверяет существование проблемы по ID.

    Назначение:
        Валидирует, что проблема существует в базе данных по заданному ID.
    Параметры:
        problem_id: Целое число, представляющее ID проблемы для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная проблема, если она существует.
    Исключения:
        HTTPException: Если проблема не найдена.
    """

    try:
        await problem_crud.get_or_404(session, problem_id)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_PROBLEM_NOT_FOUND)
