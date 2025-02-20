from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.constants import TEXT_ERROR_NOT_FOUND
from src.crud import CRUDBase
from src.problems.models.problem_models import Problem


class CRUDProblem(CRUDBase):
    """CRUD для операций с моделями Problem."""

    async def get_with_owner(self, session: AsyncSession, problem_id: int) -> Problem:
        """
        Функция получения объекта Problem со связанным с ним объектом пользователя UserTabit.
        Возвращает объект модели Problem.

        problem_id: path-параметр, соответствующий id запрашиваемой проблемы
        """
        problem = await session.execute(
            select(self.model)
            .where(self.model.id == problem_id)
            .options(selectinload(self.model.owner))
        )
        problem = problem.scalar_one_or_none()
        if not problem:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=TEXT_ERROR_NOT_FOUND)
        return problem


problem_crud = CRUDProblem(Problem)
