from datetime import date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.problems.models.enums import StatusTask
from src.constants import ZERO


class TaskBaseSchema(BaseModel):
    """Базовая схема для задач"""

    name: str
    description: Optional[str] = None
    date_completion: date
    problem_id: Optional[int] = None

    @field_validator('date_completion')
    @classmethod
    def _validator_date_in_future(cls, value: date) -> date:
        """Дата должна быть в будущем"""
        if value < date.today():
            raise ValueError('Дата должна быть в будущем')
        return value

    @field_validator('name')
    @classmethod
    def _validator_not_empty(cls, value: str) -> str:
        """Значение не может быть пустой строкой"""
        if value == '':
            raise ValueError('Имя не может быть пустой строкой')
        return value

    class Config:
        populate_by_name = True


class TaskResponseSchema(TaskBaseSchema):
    """Схема задачи для ответа"""

    id: int
    owner_id: UUID
    status: StatusTask
    executors: List[UUID]  # Ожидаем список UUID
    transfer_counter: int
    file: Optional[List[str]] = None

    @field_validator('executors', mode='before')
    def transform_executors(cls, executors):
        """Преобразует список объектов AssociationUserTask в список UUID."""
        if executors and isinstance(executors[ZERO], object):
            return [executor.left_id for executor in executors]
        return executors

    class Config:
        from_attributes = True


class TaskCreateSchema(TaskBaseSchema):
    """Схема для создания задачи"""

    owner_id: Optional[UUID] = None
    status: Optional[StatusTask] = None
    transfer_counter: int = ZERO
    file: Optional[List[str]] = None
    executors: Optional[List[UUID]] = None

    class Config:
        from_attributes = True


class TaskUpdateSchema(BaseModel):
    """Схема для обновления задачи"""

    name: Optional[str] = None
    description: Optional[str] = None
    date_completion: Optional[date] = None
    executors: Optional[List[UUID]] = None
    status: Optional[StatusTask] = None

    @field_validator('date_completion')
    @classmethod
    def validate_future_date(cls, value: Optional[date]) -> Optional[date]:
        if value and value < date.today():
            raise ValueError('Дата должна быть в будущем')
        return value

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value.strip() == '':
            raise ValueError('Имя не может быть пустой строкой')
        return value
