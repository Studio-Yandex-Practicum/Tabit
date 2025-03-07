from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.constants import ERROR_TASK_FOR_PROBLEM_NOT_FOUND, ERROR_TASK_NOT_FOUND
from src.problems.crud import task_crud


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
