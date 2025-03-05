from typing import Union

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.companies.models import Company
from src.constants import (
    DEFAULT_AUTO_COMMIT,
    TEXT_ERROR_SERVER_CREATE,
    TEXT_ERROR_SERVER_CREATE_LOG,
    TEXT_ERROR_SERVER_UPDATE,
    TEXT_ERROR_SERVER_UPDATE_LOG,
    TEXT_ERROR_UNIQUE,
    TEXT_ERROR_UNIQUE_CREATE_LOG,
    TEXT_ERROR_UNIQUE_UPDATE_LOG,
)
from src.crud import CRUDBase
from src.logger import logger
from src.problems.models import Problem, Task
from src.problems.models.association_models import AssociationUserTask
from src.problems.models.file_path_models import FileTask
from src.problems.schemas.task import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema
from src.users.models import UserTabit


class CRUDTask(CRUDBase):
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
            return task  # type: ignore
        return TaskResponseSchema.model_validate(task)

    async def create(
        self,
        session: AsyncSession,
        obj_in: TaskCreateSchema,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> TaskResponseSchema:
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
        try:
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
            if auto_commit:
                await session.commit()
                await session.refresh(new_task)
            await session.execute(
                select(Task)
                .filter_by(id=new_task.id)
                .options(selectinload(Task.executors), selectinload(Task.file))
            )
            return TaskResponseSchema.model_validate(new_task)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_UNIQUE_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TEXT_ERROR_UNIQUE,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_CREATE,
            )

    async def update(
        self,
        session: AsyncSession,
        db_obj: Task,
        obj_in: TaskUpdateSchema,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> TaskResponseSchema:
        """Обновляет задачу.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            db_obj: Объект задачи для обновления.
            obj_in: Данные для обновления задачи.
            auto_commit: Автоматически коммитить изменения (по умолчанию True).

        Returns:
            TaskResponseSchema: Обновлённая задача.

        Raises:
            HTTPException: Если произошла ошибка при обновлении задачи.
        """
        try:
            old_date_completion = db_obj.date_completion
            update_data = obj_in.model_dump(exclude_unset=True)
            executors_data = update_data.pop('executors', None)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            if executors_data is not None:
                await session.execute(
                    delete(AssociationUserTask).where(AssociationUserTask.right_id == db_obj.id)
                )
                for executor_id in executors_data:
                    association = AssociationUserTask(left_id=executor_id, right_id=db_obj.id)
                    session.add(association)
            # Увеличиваем счётчик передач, если дата завершения изменилась
            if db_obj.date_completion > old_date_completion:
                db_obj.transfer_counter += 1
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
            return TaskResponseSchema.model_validate(db_obj)

        except IntegrityError as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_UNIQUE_UPDATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TEXT_ERROR_UNIQUE,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_UPDATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_UPDATE,
            )


task_crud = CRUDTask(Task)
