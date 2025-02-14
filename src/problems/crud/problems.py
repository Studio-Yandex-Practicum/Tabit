from sqlalchemy.ext.asyncio import AsyncSession
from src.crud import CRUDBase
from src.problems.models import Problem
from src.problems.schemas.problem import ProblemUpdateSchema


class CRUDProblem(CRUDBase):
    """CRUD операции для модели проблемы."""

    async def update_problem(
        self, session: AsyncSession, problem_id: int, problem_update: ProblemUpdateSchema
    ) -> Problem:
        """Обновление проблемы.

        Назначение:
            Обновляет данные проблемы в базе данных по её ID.
            Перед обновлением проверяет существование проблемы.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_id: ID проблемы для обновления.
            problem_update: Схема с данными для обновления проблемы.
        Возвращаемое значение:
            Обновленный объект проблемы.
        """
        db_obj = await self.get_or_404(session, problem_id)
        return await self.update(session, db_obj, problem_update)

    async def delete_problem(self, session: AsyncSession, problem_id: int) -> None:
        """Удаление проблемы.

        Назначение:
            Удаляет проблему из базы данных по её ID.
            Перед удалением проверяет существование проблемы.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_id: ID проблемы для удаления.
        Возвращаемое значение:
            None
        """
        db_obj = await self.get_or_404(session, problem_id)
        await self.remove(session, db_obj)


problem_crud = CRUDProblem(Problem)
