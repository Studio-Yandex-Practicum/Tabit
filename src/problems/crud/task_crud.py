from typing import Union

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi.encoders import jsonable_encoder
from src.companies.models import Company
from src.constants import DEFAULT_AUTO_COMMIT, TextError
from src.crud import CRUDBase, CRUDBaseWithAssociations
from src.logger import logger
from src.problems.models import Problem, Task
from src.problems.models.association_models import AssociationUserTask
from src.problems.models.file_path_models import FileTask
from src.problems.schemas.task import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema
from src.users.models import UserTabit
from src.problems.models.enums import StatusTask
from src.constants import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_PROBLEM,
    LENGTH_NAME_USER,
    LENGTH_SLUG,
    LENGTH_SMALL_NAME,
    ZERO,
)

class CRUDTask(CRUDBaseWithAssociations):
    """CRUD операции для модели задачи."""

    async def get_by_company_and_problem(
        self, session: AsyncSession, company_slug: str, problem_id: int
    ) -> list[TaskResponseSchema]:
        """
        Получает все задачи по company_slug и problem_id.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            problem_id: ID проблемы.
            company_slug: Уникальный идентификатор компании.

        Returns:
            TaskResponseSchema: Список задач для данной проблемы.
        """
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
    ) -> Union[Task, TaskResponseSchema]:
        """
        Получает задачу по id с проверкой принадлежности к компании и проблеме.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            problem_id: ID проблемы.
            company_slug: Уникальный идентификатор компании.
            task_id: ID задачи.
            as_object: Данные для обновления задачи.

        Returns:
            TaskResponseSchema: Конктетная задача.
        """
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

    async def create_task_with_executors(
        self,
        session: AsyncSession,
        task_in: TaskCreateSchema,
        owner: UserTabit,
        problem: Problem,
    ) -> Task:
        """Создает новую задачу.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            obj_in: Данные для создания задачи.
            auto_commit: Автоматически коммитить изменения (по умолчанию True).

        Returns:
            TaskResponseSchema: Созданная задача.

        Raises:
            HTTPException: Если произошла ошибка при создании задачи.
        """
        task_data = task_in.model_dump()
        executors = task_data.pop('executors') if 'executors' in task_data else None
        default_data = {
            'problem_id': problem.id,
            'owner_id': owner.id,
            'status': StatusTask.NEW,
            'transfer_counter': ZERO,
        }
        task_data.update(default_data)
        task_db = self.model(**task_data)
        try:
            session.add(task_db)
            await session.flush()
            if executors:
                executors = set(executors)
                associations_data = [
                    self.associations_model(
                        left_id=executor,
                        right_id=task_db.id,
                    ) for executor in executors
                ]
                session.add_all(associations_data)
            await session.commit()
            await session.refresh(task_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_DELETE_LOG} {self.model.__name__}: {error}')
            raise error
        return task_db

    async def update_task(
        self,
        session: AsyncSession,
        task_db: Task,
        task_in: TaskUpdateSchema,
    ) -> Task:
        """Обновляет задачу.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            task_id: Идентификатор задачи для обновления.
            obj_in: Данные для обновления задачи.
            company_slug: Уникальный идентификатор компании.
            problem_id: Идентификатор проблемы.
            auto_commit: Автоматически коммитить изменения (по умолчанию True).

        Returns:
            TaskResponseSchema: Обновлённая задача.

        Raises:
            HTTPException: Если задача не найдена или произошла ошибка при обновлении.
        """
        task_data = jsonable_encoder(task_db)
        task_update_data = task_in.model_dump(exclude_unset=True)
        executors = task_update_data.pop('executors') if 'executors' in task_update_data else None

        old_data_task = task_db.date_completion

        for field in task_data:
            if field in task_update_data:
                setattr(task_db, field, task_update_data[field])

        if old_data_task < task_db.date_completion:
            task_db.transfer_counter += 1

        try:
            session.add(task_db)
            await session.flush()

            if executors is not None:
                executors = set(executors)

                add_rows, delete_rows = self.get_data_associations_for_updata(
                    task_data['executors'],
                    executors,
                )

                if add_rows:
                    associations_data = [
                        self.associations_model(
                            left_id=executor,
                            right_id=task_db.id,
                        ) for executor in add_rows
                    ]
                    session.add_all(associations_data)

                await session.execute(
                    delete(self.associations_model).where(
                        self.associations_model.right_id == task_db.id,
                        self.associations_model.left_id.in_(delete_rows),
                    )
                )

            await session.commit()
            await session.refresh(task_db)

        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
            raise error

        return task_db


task_crud = CRUDTask(Task, AssociationUserTask)
