from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config.logging import logger
from src.crud import CRUDBaseWithAssociations
from src.crud.constants import ZERO, TextError
from src.models import AssociationUserTask, Company, CompanyUser, Problem, StatusTask, Task
from src.schemas import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema


class CRUDTask(CRUDBaseWithAssociations):
    """CRUD операции для модели задачи."""

    # TODO LOST: используется в валидаторе, который нигде не используется.
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
            .join(CompanyUser.company)
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

    async def create_task_with_executors(
        self,
        session: AsyncSession,
        task_in: TaskCreateSchema,
        owner: CompanyUser,
        problem: Problem,
    ) -> Task:
        """Создает новую задачу.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            task_in: Данные для создания задачи.
            owner: экземпляр модели пользователя, автор задачи.
            problem: экземпляр модели проблемы, для решения который назначается задача.
        Возвращает:
            Созданная задача.

        Возможные ошибки:
            HTTPException: Если произошла ошибка при создании задачи.
        """
        task_data = task_in.model_dump()
        executors = task_data.pop('executors') if 'executors' in task_data else []
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
                    )
                    for executor in executors
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
        """
        Для изменения записи в таблице Проблемы.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            task_db: экземпляр модели задачи.
            task_in: данные для изменения в виде схемы.
        Возвращает:
            Экземпляр модели проблемы после изменения.

        Возможные ошибки:
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
                        )
                        for executor in add_rows
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
