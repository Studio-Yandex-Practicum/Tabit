from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.problems.models.enums import StatusTask


class TaskBaseSchema(BaseModel):
    """Базовая схема для задач"""

    name: str
    description: Optional[str] = None
    date_completion: date
    executor: List[UUID]

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


class TaskResponseSchema(TaskBaseSchema):
    """Схема задачи для ответа"""

    id: int
    problem_id: int
    owner_id: UUID
    status: StatusTask
    transfer_counter: int
    file: Optional[List[str]] = None


class TaskCreateSchema(TaskBaseSchema):
    """Схема для создания задачи"""

    pass


class TaskUpdateSchema(TaskBaseSchema):
    """Схема для обновления задачи"""

    name: Optional[str] = None
    description: Optional[str] = None
    date_completion: Optional[date] = None
    executor: Optional[List[UUID]] = None
    status: Optional[StatusTask] = None
