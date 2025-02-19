from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.problems.models import Problem
from src.problems.models.association_models import AssociationUserTask
from src.problems.models.file_path_models import FileTask
from src.problems.schemas.task import TaskCreateSchema, TaskResponseSchema
from src.users.models import UserTabit
from src.crud import CRUDBase
from src.problems.models import Task
from src.companies.models import Company
# from src.problems.models.enums import StatusTask


class CRUDTask(CRUDBase):
    """CRUD операции для модели задачи."""

    async def get_by_company_and_problem(
        self, session: AsyncSession, company_slug: str, problem_id: int
    ):
        """Получает все задачи по company_slug и problem_id."""

        # query = (
        #     select(self.model)
        #     .join(  # Соединяем Task -> Problem
        #         Problem, Problem.id == self.model.problem_id
        #     )
        #     .join(  # Присоединяем UserTabit через Task.executors (минуя связную таблицу)
        #         UserTabit, UserTabit.id.in_(
        #             select(AssociationUserTask.left_id).where(
        #                 AssociationUserTask.right_id == self.model.id
        #             )
        #         )
        #     )
        #     .join(  # Присоединяем Company через UserTabit
        #         Company, Company.id == UserTabit.company_id
        #     )
        #     .where(Company.slug == company_slug)
        #     .where(self.model.problem_id == problem_id)
        #     .options(
        #         selectinload(self.model.executors),  # Подгружаем исполнителей
        #         selectinload(self.model.file),       # Подгружаем файлы
        #     )
        # )

        query = (
            select(self.model)
            .join(Problem, Problem.id == self.model.problem_id)
            .join(UserTabit, UserTabit.id == Problem.owner_id)
            .join(Company, Company.id == UserTabit.company_id)
            .where(Company.slug == company_slug)
            .where(self.model.problem_id == problem_id)
            .options(
                selectinload(self.model.file),
                selectinload(self.model.executors),  # Загружаем связанные данные
            )
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        # Преобразуем ORM-объекты в Pydantic-модели
        return [TaskResponseSchema.model_validate(task) for task in tasks]

        # task_ids = [task.id for task in tasks]

        # executor_query = (
        #     select(AssociationUserTask.left_id, AssociationUserTask.right_id)
        #     .where(AssociationUserTask.right_id.in_(task_ids))
        # )
        # executor_result = await session.execute(executor_query)

        # # Получаем список кортежей (исполнитель_id, задача_id)
        # executor_pairs = executor_result.all()

        # # Преобразуем в task_id -> list of executors
        # executor_map = {task_id: [] for task_id in task_ids}
        # for executor_id, task_id in executor_pairs:
        #     if task_id in executor_map:
        #         executor_map[task_id].append(uuid.UUID(executor_id))  # Преобразуем ID исполнителя в строку
        # print(executor_map)
        # # Присваиваем список исполнителей каждой задаче
        # for task in tasks:
        #     task.executors = executor_map.get(task.id, [])

        # print(task.owner_id)
        # Получаем ID задач
        # task_ids = [task.id for task in tasks]

        # if task_ids:
        # Запрос на получение исполнителей для этих задач
        # executor_query = (
        #     select(AssociationUserTask.left_id)
        #     .where(AssociationUserTask.right_id.in_(task_ids))
        # )
        # executor_result = await session.execute(executor_query)

        # # Получаем список всех исполнителей (left_id)
        # executors = executor_result.scalars().all()  # Это будет список всех left_id
        # # print(executors)
        # # Преобразуем результат в формат task_id -> list of executors
        # executor_map = {task_id: [] for task_id in task_ids}
        # # list_exec = []
        # for executor_id in executors:
        #     # task_id = executor_id  # Для каждой строки добавляем task_id
        #     print(executor_id)
        #     # print(task_id)
        #     # if task_id in executor_map:
        #     executor_map['task_id'].append(str(executor_id))  # Добавляем строковое представление исполнителя
        # # print(executor_map)
        # # Присваиваем список исполнителей каждой задаче
        # for task in tasks:
        #     task.executors = executor_map.get(task.id, [])
        # print(task.executors)

        # query = (
        #     select(self.model)
        #     .join(Problem, Problem.id == self.model.problem_id)
        #     .join(UserTabit, UserTabit.id == Problem.owner_id)
        #     .join(Company, Company.id == UserTabit.company_id)
        #     .where(Company.slug == company_slug)
        #     .where(self.model.problem_id == problem_id)
        #     .options(
        #         selectinload(self.model.executors),  # Загружаем исполнителей
        #         selectinload(self.model.file),
        #     )
        # )
        # # query = select(AssociationUserTask.left_id)
        # # print(query)
        # result = await session.execute(query)
        # tasks = result.scalars().all()
        # # print(tasks)
        # return tasks

    async def get_task_by_id(
        self, session: AsyncSession, company_slug: str, problem_id: int, task_id: int
    ):
        query = (
            select(self.model)
            .join(Problem, Problem.id == self.model.problem_id)
            .join(UserTabit, UserTabit.id == Problem.owner_id)
            .join(Company, Company.id == UserTabit.company_id)
            .where(Company.slug == company_slug)
            .where(self.model.problem_id == problem_id)
            .where(self.model.id == task_id)
            .options(
                selectinload(self.model.file),
                selectinload(self.model.executors),  # Загружаем связанные данные
            )
        )

        result = await session.execute(query)
        task = result.scalars().first()

        if task:
            # Преобразуем ORM-объект в Pydantic-модель
            return TaskResponseSchema.model_validate(task)
        return None
        # task = await session.execute(select(Task).where(Task.id == task_id).options(selectinload(self.model.executors)))
        # task = task.scalars().first()
        # if task:
        # Преобразуем ORM-объект в Pydantic-модель
        #     return TaskResponseSchema.model_validate(task)
        # return None
        # return task
        # task = select(Task).where(Task.id == task_id)
        # result = await session.execute(query)

    async def create_task(self, session: AsyncSession, obj_in: TaskCreateSchema):
        """Создает новую задачу."""
        new_task = Task(**obj_in.model_dump(exclude={'executors', 'file'}))
        session.add(new_task)
        await session.flush()  # Получаем ID задачи без коммита

        # Добавляем файлы (если есть)
        if obj_in.file:
            new_task.file = [FileTask(url=url, task_id=new_task.id) for url in obj_in.file]

        # Добавляем исполнителей (если есть)
        if obj_in.executors:
            associations = [
                AssociationUserTask(left_id=executor_id, right_id=new_task.id)
                for executor_id in obj_in.executors
            ]
            session.add_all(associations)

        await session.commit()
        await session.refresh(new_task)  # Загружаем обновлённый объект
        # return None
        return TaskResponseSchema.model_validate(new_task)

    # async def update_task(
    #         self,
    #         session: AsyncSession,
    #         task_id: int,
    #         task_data: TaskUpdateSchema) -> Task:
    #     query = select(Task).where(Task.id == task_id)
    #     result = await session.execute(query)
    #     task = result.scalars().first()

    #     if not task:
    #         raise HTTPException(status_code=404, detail="Задача не найдена")

    #     for key, value in task_data.model_dump(exclude_unset=True).items():
    #         setattr(task, key, value)

    #     await session.commit()
    #     await session.refresh(task)
    #     return task


task_crud = CRUDTask(Task)
