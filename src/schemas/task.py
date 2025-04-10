from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models import StatusTask
from src.schemas.validators.task import (
    validate_date_in_future,
    validate_name,
)


class TaskBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для задач.

    Назначение:
        Определяет базовые поля и их типы для работы с данными задач.
    Параметры:
        description: Описание задачи (опционально).
    """

    description: str | None = None
    # TODO: Надо реализовать добавление файлов в встречу


class TaskSchemaMixin:
    """
    Миксин для схем Задач, с валидаторами.

    Параметры:
        executors: Список идентификаторов исполнителей.
    """

    executors: list[UUID] | None = []

    model_config = ConfigDict(extra='forbid', str_min_length=1)

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


class ExecutorsResponseSchema(BaseModel):
    """Схема исполнителя задачи.

    Назначение:
        Определяет структуру данных для ответа с информацией о исполнителе задачи.
    Параметры:
        member_id: UUID исполнителя задачи.
    """

    executor_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class TaskResponseSchema(BaseModel):
    """
    Pydantic-схема для данных о задаче из БД.

    Назначение:
        Используется для сериализации данных о задаче при получении из БД.
    Параметры:
        id: Идентификатор задачи.
        name: Название задачи.
        description: Описание задачи (опционально).
        date_completion: Дата выполнения задачи
        owner_id: Идентификатор создателя задачи.
        problem_id: Идентификатор проблемы, для которой создана задача.
        executors: Список идентификаторов исполнителей, реализованны через схему.
        status: Статус задачи.
        transfer_counter: Счётчик переноса даты выполнения задачи.
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


class TaskCreateSchema(TaskSchemaMixin, TaskBaseSchema):
    """
    Pydantic-схема для данных о задаче из БД.

    Назначение:
        Используется для сериализации данных о задаче при создании записи в БД.
    Параметры:
        name: Название задачи.
        description: Описание задачи (опционально).
        date_completion: Дата выполнения задачи
        executors: Список идентификаторов исполнителей.
    """

    name: str
    date_completion: date


class TaskUpdateSchema(TaskSchemaMixin, TaskBaseSchema):
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
    date_completion: date | None = None
    status: StatusTask | None = None
