from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.models import TaskStatus


class TaskBaseSchema(BaseModel):
    """Базовая схема задачи.

    Определяет базовые поля задачи.
    Поля:
        description: Описание задачи (опционально).
    """
    description: str | None = None
    # TODO: Реализовать добавление файлов в задачу

    model_config = ConfigDict(extra='forbid')


class ExecutorsResponseSchema(BaseModel):
    """Схема исполнителя задачи.

    Определяет данные исполнителя для ответа.
    Поля:
        executor_id: UUID исполнителя.
    """
    executor_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class TaskResponseSchema(TaskBaseSchema):
    """Схема задачи для ответа.

    Определяет данные задачи из БД.
    Поля:
        id: Идентификатор задачи.
        name: Название задачи.
        description: Описание (опционально).
        date_completion: Дата выполнения.
        owner_id: UUID создателя.
        problem_id: ID проблемы.
        executors: Список исполнителей.
        status: Статус задачи.
        transfer_counter: Счетчик переноса даты.
    """
    id: int
    name: str
    date_completion: date
    owner_id: UUID
    problem_id: int
    executors: list[ExecutorsResponseSchema]
    status: TaskStatus
    transfer_counter: int

    model_config = ConfigDict(from_attributes=True)


class TaskCreateSchema(TaskBaseSchema):
    """Схема для создания задачи.

    Определяет данные для создания задачи.
    Поля:
        name: Название (не пустое, без пробелов).
        date_completion: Дата выполнения (в будущем).
        executors: Список UUID исполнителей (опционально).
    """
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    date_completion: Annotated[
        date,
        Field(..., ge=date.today())
    ]
    executors: list[UUID] | None = []

    model_config = ConfigDict(extra='forbid')


class TaskUpdateSchema(TaskBaseSchema):
    """Схема для обновления задачи.

    Определяет данные для обновления задачи.
    Поля:
        name: Название (опционально, не пустое, без пробелов).
        description: Описание (опционально).
        date_completion: Дата выполнения (опционально, в будущем).
        executors: Список UUID исполнителей (опционально).
        status: Статус задачи (опционально).
    """
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = None
    date_completion: Annotated[
        date,
        Field(None, ge=date.today())
    ] | None = None
    executors: list[UUID] | None = None
    status: TaskStatus | None = None

    model_config = ConfigDict(extra='forbid')