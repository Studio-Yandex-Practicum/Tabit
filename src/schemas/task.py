from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models import TaskStatus
from src.schemas.annotations import DescriptionField, NameField, OptionalNameField
from src.schemas.constants import Title


class TaskBaseSchema(BaseModel):
    """
    Базовая схема задачи.

    Определяет общие поля для схем задач.

    Атрибуты:
        description (Optional[str]): Описание задачи.
    """

    description: DescriptionField = Field(None, title=Title.TASK_DESCRIPTION)
    # TODO: Реализовать добавление файлов в задачу

    model_config = ConfigDict(extra='forbid')


class ExecutorsResponseSchema(BaseModel):
    """
    Схема исполнителя задачи.

    Используется для представления данных об исполнителе задачи в ответах API.

    Атрибуты:
        executor_id (UUID): Идентификатор исполнителя.
    """

    executor_id: UUID = Field(validation_alias='left_id', title=Title.TASK_EXECUTOR_ID)

    model_config = ConfigDict(from_attributes=True)


class TaskResponseSchema(TaskBaseSchema):
    """
    Схема задачи для ответа.

    Используется для возврата данных о задаче из базы данных через API.

    Атрибуты:
        id (int): Идентификатор задачи.
        name (str): Название задачи.
        description (Optional[str]): Описание задачи.
        date_completion (date): Дата выполнения задачи.
        owner_id (UUID): Идентификатор создателя задачи.
        problem_id (int): Идент
        executors (list[ExecutorsResponseSchema]): Список исполнителей задачи.
        status (TaskStatus): Статус задачи.
        transfer_counter (int): Счетчик переноса даты выполнения.
        created_at (date): Дата создания задачи.
        updated_at (date): Дата последнего обновления задачи.
    """

    id: int = Field(..., title=Title.TASK_ID)
    name: str = Field(..., title=Title.TASK_NAME)
    date_completion: date = Field(..., title=Title.TASK_DATE_COMPLETION)
    owner_id: UUID = Field(..., title=Title.TASK_OWNER_ID)
    problem_id: int = Field(..., title=Title.TASK_PROBLEM_ID)
    executors: list[ExecutorsResponseSchema] = Field(..., title=Title.TASK_EXECUTORS)
    status: TaskStatus = Field(..., title=Title.TASK_STATUS)
    transfer_counter: int = Field(..., title=Title.TASK_TRANSFER_COUNTER)
    created_at: date = Field(..., title=Title.TASK_CREATED_AT)
    updated_at: date = Field(..., title=Title.TASK_UPDATED_AT)

    model_config = ConfigDict(from_attributes=True)


class TaskCreateSchema(TaskBaseSchema):
    """
    Схема для создания задачи.

    Используется для добавления новой задачи через API.

    Атрибуты:
        name (str): Название задачи.
        date_completion (date): Дата выполнения задачи (должна быть в будущем).
        executors (Optional[list[UUID]]): Список идентификаторов исполнителей.
        description (Optional[str]): Описание задачи.
    """

    name: NameField = Field(..., title=Title.TASK_NAME)
    date_completion: Annotated[date, Field(..., ge=date.today(), title=Title.TASK_DATE_COMPLETION)]
    executors: list[UUID] | None = Field(default=[], title=Title.TASK_EXECUTORS)

    model_config = ConfigDict(extra='forbid')


class TaskUpdateSchema(TaskBaseSchema):
    """
    Схема для обновления задачи.

    Используется для изменения данных задачи через API.

    Атрибуты:
        name (Optional[str]): Название задачи.
        description (Optional[str]): Описание задачи.
        date_completion (Optional[date]): Дата выполнения задачи (должна быть в будущем).
        executors (Optional[list[UUID]]): Список идентификаторов исполнителей.
        status (Optional[TaskStatus]): Статус задачи.
    """

    name: OptionalNameField = Field(None, title=Title.TASK_NAME)
    date_completion: (
        Annotated[date, Field(None, ge=date.today(), title=Title.TASK_DATE_COMPLETION)] | None
    ) = None
    executors: list[UUID] | None = Field(None, title=Title.TASK_EXECUTORS)
    status: TaskStatus | None = Field(None, title=Title.TASK_STATUS)

    model_config = ConfigDict(extra='forbid')
