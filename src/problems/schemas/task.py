from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.constants import ZERO
from src.problems.models.enums import StatusTask
from src.problems.validators.task_validators import (
    validate_date_in_future,
    validate_executors,
    validate_name,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для задач.

    Назначение:
        Определяет базовые поля и их типы для работы с данными задач.
    Параметры:
        name: Название задачи.
        description: Описание задачи (опционально).
        date_completion: Дата завершения задачи.
        problem_id: Идентификатор связанной проблемы (опционально).
    """

    name: str
    description: Optional[str] = None
    date_completion: date
    problem_id: Optional[int] = None

    @field_validator('date_completion')
    @classmethod
    def validate_date_in_future(cls, value: date) -> date:
        """Валидирует дату завершения задачи."""
        return validate_date_in_future(value)

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        """Валидирует название задачи."""
        return validate_name(value)

    class Config:
        populate_by_name = True


class ExecutorsResponseSchema(BaseModel):

    executor_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class TaskResponseSchema(BaseModel):
    """
    Pydantic-схема для данных о задаче из БД.

    Назначение:
        Используется для сериализации данных о задаче при получении из БД.
    Параметры:
        id: Идентификатор задачи.
        owner_id: Идентификатор создателя задачи.
        status: Статус задачи.
        executors: Список идентификаторов исполнителей.
        transfer_counter: Счётчик передачи задачи.
        file: Список файлов, связанных с задачей (опционально).
    """

    id: int
    name: str
    description: str | None
    date_completion: date
    owner_id: UUID
    problem_id: int
    executors: list[ExecutorsResponseSchema]
    status: StatusTask
    transfer_counter: int

    model_config = ConfigDict(from_attributes=True)

    # @field_validator('executors', mode='before')
    # def transform_executors(cls, executors):
    #     """
    #     Преобразует список объектов AssociationUserTask в список UUID.

    #     Назначение:
    #         Преобразует список объектов в список UUID для корректной сериализации.
    #     Параметры:
    #         executors: Список объектов или UUID.
    #     Возвращаемое значение:
    #         Список UUID.
    #     """
    #     if executors and isinstance(executors[ZERO], object):
    #         return [executor.left_id for executor in executors]
    #     return executors

    # class Config:
    #     from_attributes = True


class TaskCreateSchema(BaseModel):
    """Схема для создания задачи"""

    name: str
    description: str | None
    date_completion: date
    executors: list[UUID] | None = []

    @field_validator('date_completion')
    @classmethod
    def validate_date_in_future(cls, value: date) -> date:
        """Валидирует дату завершения задачи."""
        return validate_date_in_future(value)

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        """Валидирует название задачи."""
        return validate_name(value)

    model_config = ConfigDict(extra='forbid')


class TaskUpdateSchema(BaseModel):
    """
    Pydantic-схема для обновления задачи.

    Назначение:
        Используется для валидации данных при обновлении информации о задаче.
    Параметры:
        name: Название задачи (опционально).
        description: Описание задачи (опционально).
        date_completion: Дата завершения задачи (опционально).
        executors: Список идентификаторов исполнителей (опционально).
        status: Статус задачи (опционально).
    """

    name: str | None = None
    description: str | None = None
    date_completion: date | None = None
    executors: list[UUID] | None = []
    status: StatusTask | None = None

    @field_validator('date_completion')
    @classmethod
    def validate_future_date(cls, value: Optional[date]) -> Optional[date]:
        """Валидирует дату завершения задачи."""
        if value is not None:
            return validate_date_in_future(value)
        return value

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Валидирует название задачи."""
        if value is not None:
            return validate_name(value)
        return value
