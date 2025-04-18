from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import task_crud
from src.features_v1.constants import ERROR_TASK_NOT_FOUND, TextError
from src.models import Task, TaskStatus


async def check_task_exists(task_id: int, session: AsyncSession):
    """Проверяет, существует ли задача в базе данных.

    Args:
        task_id: Идентификатор задачи.
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если задача не найдена.
    """
    return await task_crud.get_or_404(session, task_id, message=ERROR_TASK_NOT_FOUND)


def validate_task_completed(task: Task):
    """
    Валидатор, проверит что встреча не проведена.

    Иначе ошибка 422
    """
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.TASK_COMPLETED,
        )