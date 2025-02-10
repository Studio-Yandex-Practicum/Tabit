from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.crud import CRUDBase
from src.problems.models import Task
from src.companies.models import Company
from sqlalchemy.orm import selectinload
# from src.problems.models.association_models import AssociationUserTask


class CRUDTask(CRUDBase):
    """CRUD операции для модели задачи."""

    async def get_by_company_and_problem(
        self, session: AsyncSession, company_slug: str, problem_id: int
    ):
        """Получает все задачи по company_slug и problem_id."""
        query = (
            select(self.model)
            .join(self.model.problem)
            .where(Company.slug == company_slug)
            .where(self.model.problem_id == problem_id)
            .options(
                selectinload(self.model.executors),
                selectinload(self.model.file),
            )
        )
        result = await session.execute(query)
        tasks = result.scalars().all()
        return tasks


task_crud = CRUDTask(Task)
