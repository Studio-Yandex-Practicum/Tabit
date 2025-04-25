import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.validators import task_validators
from src.features_v1.constants import TextError
from src.models import TaskStatus


@pytest.mark.asyncio
async def test_check_task_exists_success():
    session = AsyncMock(spec=AsyncSession)
    task = MagicMock()
    task_id = 1

    # Подменяем task_crud.get_or_404
    task_validators.task_crud.get_or_404 = AsyncMock(return_value=task)

    result = await task_validators.check_task_exists(task_id, session)

    assert result == task
    task_validators.task_crud.get_or_404.assert_awaited_once_with(
        session, task_id, message=task_validators.ERROR_TASK_NOT_FOUND
    )


@pytest.mark.asyncio
async def test_check_task_exists_not_found():
    session = AsyncMock(spec=AsyncSession)
    task_id = 1

    # Симулируем ошибку при получении
    task_validators.task_crud.get_or_404 = AsyncMock(side_effect=HTTPException(status_code=404))

    with pytest.raises(HTTPException) as exc_info:
        await task_validators.check_task_exists(task_id, session)

    assert exc_info.value.status_code == 404


def test_validate_task_completed_raises():
    task = MagicMock()
    task.status = TaskStatus.COMPLETED

    with pytest.raises(HTTPException) as exc_info:
        task_validators.validate_task_completed(task)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == TextError.TASK_COMPLETED


def test_validate_task_completed_ok():
    task = MagicMock()
    task.status = TaskStatus.IN_PROGRESS

    # Не должно выбрасываться исключение
    task_validators.validate_task_completed(task)