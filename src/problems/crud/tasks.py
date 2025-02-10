from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.problems.models import Task, AssociationUserTask
from src.problems.models.enums import StatusTask
from src.problems.schemas.task import TaskCreateSchema


class CRUDTask(CRUDBase):
    """CRUD операции для модели задачи."""

    async def create(self, session: AsyncSession, obj_in: TaskCreateSchema) -> Task:
        # Создаем копию данных и модифицируем их
        obj_data = obj_in.model_dump()
        executors = obj_data.pop('executors', [])
        obj_data['status'] = StatusTask.NEW

        # Создаем задачу
        db_obj = self.model(**obj_data)
        session.add(db_obj)

        # Добавляем исполнителей
        for executor_id in executors:
            db_obj.executors.append(AssociationUserTask(left_id=executor_id))

        await session.commit()
        await session.refresh(db_obj)
        return db_obj


task_crud = CRUDTask(Task)
