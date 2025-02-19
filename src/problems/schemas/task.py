from datetime import date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.problems.models.enums import StatusTask


class FileTaskShema(BaseModel):
    pass


# class ExecutorSchema(BaseModel):
#     left_id: UUID
#     right_id: int

#     class Config:
#         populate_by_name = True


class TaskBaseSchema(BaseModel):
    """Базовая схема для задач"""

    name: str
    description: Optional[str] = None
    date_completion: date

    @field_validator('date_completion')
    @classmethod
    def _validator_date_in_future(cls, value: date) -> date:
        """Дата должна быть в будущем"""
        if value < date.today():
            raise ValueError('Date must be in the future')
        return value

    @field_validator('name')
    @classmethod
    def _validator_not_empty(cls, value: str) -> str:
        """Значение не может быть пустой строкой"""
        if value == '':
            raise ValueError('Name cannot be an empty string')
        return value

    class Config:
        populate_by_name = True


class TaskResponseSchema(TaskBaseSchema):
    """Схема задачи для ответа"""

    id: int
    problem_id: int
    owner_id: UUID
    status: StatusTask
    executors: List[UUID]  # Ожидаем список UUID
    transfer_counter: int
    file: Optional[List[str]] = None

    @field_validator('executors', mode='before')
    def transform_executors(cls, executors):
        """
        Преобразует список объектов
        AssociationUserTask в список UUID.
        """
        if executors and isinstance(executors[0], object):  # Проверяем, что это объекты
            return [executor.left_id for executor in executors]
        return executors

    class Config:
        from_attributes = True


class TaskCreateSchema(TaskBaseSchema):
    """Схема для создания задачи"""

    # problem_id: int  # 🔥🔥🔥ВОПРОС ПО ПОВОДУ ПОЛЯ ID И ЕГО АВТОИНКРЕМЕННОСТИ В МОДЕЛЕ СОЗДАНИЕ ОБЬЕКТА, ОШИКБКА  🔥🔥🔥 Добавляем problem_id
    transfer_counter: int = 0
    file: Optional[List[str]] = None  # Список URL файлов
    executors: Optional[List[UUID]] = None  # Список ID исполнителей

    class Config:
        from_attributes = True


class TaskUpdateSchema(BaseModel):
    """Схема для обновления задачи"""

    description: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    date_completion: Optional[date] = None
    executors: Optional[List[UUID]] = None
    status: Optional[StatusTask] = None
