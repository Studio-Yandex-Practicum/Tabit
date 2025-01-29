from datetime import date
from typing import Optional, List
from uuid import UUID

from typing_extensions import Annotated
from pydantic import BaseModel, AfterValidator

from ..models.enums import StatusTask


def date_validation(value: date) -> date:
    """Дата должна быть в будущем"""
    if value < date.today():
        raise ValueError('Date must be in the future')
    return value


def name_validation(value: str) -> str:
    """Название не может быть пустой строкой"""
    if value == '':
        raise ValueError('Name cannot be an empty string')
    return value


class TaskBase(BaseModel):
    """Базовая схема для задач"""

    name: Annotated[str, AfterValidator(name_validation)]
    description: Optional[str] = None
    date_completion: Annotated[date, AfterValidator(date_validation)]
    executor: List[UUID]


class TaskDBSchema(TaskBase):
    """Схема задачи из БД"""

    id: int
    problem_id: int
    owner_id: UUID
    status: StatusTask
    transfer_counter: int
    file: Optional[List[str]] = None


class TaskCreateSchema(TaskBase):
    """Схема для создания задачи"""

    pass


class TaskUpdateSchema(BaseModel):
    """Схема для обновления задачи"""

    name: Optional[Annotated[str, AfterValidator(name_validation)]] = None
    description: Optional[str] = None
    date_completion: Optional[Annotated[date, AfterValidator(date_validation)]] = None
    executor: Optional[List[UUID]] = None
    status: Optional[StatusTask] = None
