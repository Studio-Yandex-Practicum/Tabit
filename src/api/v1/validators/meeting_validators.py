from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.constants import ERROR_PROBLEM_NOT_FOUND
from src.problems.crud.problems import problem_crud


# TODO: Нигде не используется
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
