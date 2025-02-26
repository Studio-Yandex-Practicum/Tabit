from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.companies.models import Company
from src.crud import CRUDBase
from src.problems.models import Problem, Task
from src.problems.models.association_models import AssociationUserTask
from src.problems.models.file_path_models import FileTask
from src.problems.schemas.task import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema
from src.users.models import UserTabit


class CRUDTask(CRUDBase):
    """CRUD операции для модели задачи."""

    async def get_by_company_and_problem(
        self, session: AsyncSession, company_slug: str, problem_id: int
    ):
        """Получает все задачи по company_slug и problem_id."""
        query = (
            select(self.model)
            .join(self.model.problem)
            .join(Problem.owner)
            .join(UserTabit.company)
            .where(Company.slug == company_slug)
            .where(self.model.problem_id == problem_id)
            .options(
                selectinload(self.model.file),
                selectinload(self.model.executors),
            )
        )
        result = await session.execute(query)
        tasks = result.scalars().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]

    async def get_task_by_id(
        self,
        session: AsyncSession,
        company_slug: str,
        problem_id: int,
        task_id: int,
        as_object: bool = False,
    ):
        """Получает задачу по id с проверкой принадлежности к компании и проблеме."""
        query = (
            select(self.model)
            .join(self.model.problem)
            .join(Problem.owner)
            .join(UserTabit.company)
            .where(
                Company.slug == company_slug,
                self.model.problem_id == problem_id,
                self.model.id == task_id,
            )
            .options(
                selectinload(self.model.file),
                selectinload(self.model.executors),
            )
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        if as_object:
            return task
        return TaskResponseSchema.model_validate(task)

    async def create_task(self, session: AsyncSession, obj_in: TaskCreateSchema):
        """Создает новую задачу."""
        new_task = Task(**obj_in.model_dump(exclude={'executors', 'file'}))
        session.add(new_task)
        await session.flush()
        if obj_in.file:
            new_task.file = [FileTask(url=url, task_id=new_task.id) for url in obj_in.file]
        if obj_in.executors:
            associations = [
                AssociationUserTask(left_id=executor_id, right_id=new_task.id)
                for executor_id in obj_in.executors
            ]
            session.add_all(associations)

        await session.commit()
        await session.refresh(new_task)
        await session.execute(
            select(Task)
            .filter_by(id=new_task.id)
            .options(selectinload(Task.executors), selectinload(Task.file))
        )
        return TaskResponseSchema.model_validate(new_task)

    async def update_task(
        self, session: AsyncSession, task: Task, task_update: TaskUpdateSchema
    ) -> TaskResponseSchema:
        old_date_completion = task.date_completion
        update_data = task_update.model_dump(exclude_unset=True)
        executors_data = update_data.pop('executors', None)
        for field, value in update_data.items():
            setattr(task, field, value)
        if executors_data is not None:
            await session.execute(
                delete(AssociationUserTask).where(AssociationUserTask.right_id == task.id)
            )
            for executor_id in executors_data:
                association = AssociationUserTask(left_id=executor_id, right_id=task.id)
                session.add(association)
        if task.date_completion > old_date_completion:
            task.transfer_counter += 1
        await session.commit()
        await session.refresh(task)
        return TaskResponseSchema.model_validate(task)


task_crud = CRUDTask(Task)
