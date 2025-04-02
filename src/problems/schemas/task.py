from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.problems.models.enums import StatusTask
from src.problems.validators.task_validators import (
    validate_date_in_future,
    validate_name,
)


class TaskBaseSchema(BaseModel):
    """
    Параметры:
        description: Описание задачи (опционально).
    """

    description: str | None = None
    # TODO: Надо реализовать добавление файлов в встречу

    model_config = ConfigDict(
        title='Схема для задач', description='Определяет базовые поля для работы с данными задач'
    )


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
    """
    Параметры:
        executor_id: UUID исполнителя задачи.
    """

    executor_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема для исполнителя задач',
        description='Схема для ответа с информацией о исполнителе задачи',
    )


class TaskResponseSchema(BaseModel):
    """
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

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема для данных о задаче из БД',
        description='Схема для сериализации данных о задаче',
    )


class TaskCreateSchema(TaskSchemaMixin, TaskBaseSchema):
    """
    Параметры:
        name: Название задачи.
        date_completion: Дата выполнения задачи
    """

    name: str
    date_completion: date

    model_config = ConfigDict(
        title='Схема создания задачи',
        description='Схема для сериализации данных при создании задачи',
    )


class TaskUpdateSchema(TaskSchemaMixin, TaskBaseSchema):
    """
    Параметры:
        name: Название задачи (опционально).
        date_completion: Дата завершения задачи (опционально).
        status: Статус задачи (опционально).
    """

    name: str | None = None
    date_completion: date | None = None
    status: StatusTask | None = None

    model_config = ConfigDict(
        title='Схема для обновления задачи',
        description='Схема для валидации обновленных данных о задаче',
    )
