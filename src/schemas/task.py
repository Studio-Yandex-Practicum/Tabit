from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.models import TaskStatus
from src.schemas.constants import Length, Title

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE
    ),
]
OptionalNameStr = Annotated[
    Optional[str],
    StringConstraints(
        strip_whitespace=True, min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE
    ),
]
DescriptionStr = Annotated[
    Optional[str],
    StringConstraints(
        min_length=Length.MIN_DESCRIPTION, max_length=Length.MAX_DESCRIPTION_COMPANY
    ),
]


class TaskBaseSchema(BaseModel):
    """Базовая схема задачи.

    Определяет базовые поля задачи.
    Поля:
        description: Описание задачи (опционально).
    """

    description: DescriptionStr = Field(None, title=Title.TASK_DESCRIPTION)
    # TODO: Реализовать добавление файлов в задачу

    model_config = ConfigDict(extra='forbid')


class ExecutorsResponseSchema(BaseModel):
    """Схема исполнителя задачи.

    Определяет данные исполнителя для ответа.
    Поля:
        executor_id: UUID исполнителя.
    """

    executor_id: UUID = Field(validation_alias='left_id', title=Title.TASK_EXECUTOR_ID)

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
    """Схема для создания задачи.

    Определяет данные для создания задачи.
    Поля:
        name: Название (не пустое, без пробелов).
        date_completion: Дата выполнения (в будущем).
        executors: Список UUID исполнителей (опционально).
    """

    name: NameStr = Field(..., title=Title.TASK_NAME)
    date_completion: Annotated[date, Field(..., ge=date.today(), title=Title.TASK_DATE_COMPLETION)]
    executors: list[UUID] | None = Field(default=[], title=Title.TASK_EXECUTORS)

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

    name: OptionalNameStr = Field(None, title=Title.TASK_NAME)
    date_completion: (
        Annotated[date, Field(None, ge=date.today(), title=Title.TASK_DATE_COMPLETION)] | None
    ) = None
    executors: list[UUID] | None = Field(None, title=Title.TASK_EXECUTORS)
    status: TaskStatus | None = Field(None, title=Title.TASK_STATUS)

    model_config = ConfigDict(extra='forbid')
