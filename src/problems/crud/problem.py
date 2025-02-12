from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        return problem.scalars().first()


problem_crud = CRUDProblem(Problem)
