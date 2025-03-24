from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem
from src.problems.validators.problem_validators import validate_not_empty


class ProblemBaseSchema(BaseModel):
    """Базовая схема Проблеммы.

    Назначение:
        Определяет базовую структуру данных для проблемы.
    Параметры:
        description: Описание проблемы (опционально).
    """

    description: str | None = None
    # TODO Надо реализовать добавление файлов в проблему


class ProblemSchemaMixin:
    """
    Миксин для схем Проблемы, с полями и валидаторами.

    Параметры:
        members: список участников, из связной таблицы, оформленных через схему
    """

    members: list[UUID] | None = []

    model_config = ConfigDict(extra='forbid')

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        """Проверка, что название проблемы не пустое."""
        return validate_not_empty(value)


class MemberResponseSchema(BaseModel):
    """Схема участника Проблемы.

    Назначение:
        Определяет структуру данных для ответа с информацией о участнике Проблемы.
    Параметры:
        status: статус, отображающий участие пользователя в решении Проблемы.
        member_id: UUID участника Проблемы.
    """

    status: bool | None
    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class ProblemResponseSchema(ProblemBaseSchema):
    """Схема Проблемы для ответа.

    Назначение:
        Определяет структуру данных для ответа с информацией о проблеме.
    Параметры:
        id: Уникальный идентификатор проблемы.
        name: Название проблемы.
        description: Описание проблемы (опционально).
        color: Цвет проблемы из перечисления ColorProblem.
        type: Тип проблемы из перечисления TypeProblem.
        status: Статус проблемы из перечисления StatusProblem.
        owner_id: UUID владельца проблемы.
        company_id: id компании, с которой связана проблема.
        members: список участников, из связной таблицы, оформленных через схему
        created_at: Время создания проблемы.
        updated_at: Время последнего обновления проблемы.
    """

    id: int
    name: str
    color: ColorProblem
    type: TypeProblem
    status: StatusProblem
    owner_id: UUID
    company_id: int
    members: list[MemberResponseSchema]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProblemCreateSchema(ProblemSchemaMixin, ProblemBaseSchema):
    """Схема для создания проблемы.

    Назначение:
        Определяет структуру данных для создания новой проблемы.
    Параметры:
        name: Название проблемы.
        description: Описание проблемы (опционально).
        color: Цвет проблемы из перечисления ColorProblem.
        type: Тип проблемы из перечисления TypeProblem.
        members: список участников, из связной таблицы, оформленных через схему
    """

    name: str
    color: ColorProblem
    type: TypeProblem


class ProblemUpdateSchema(ProblemSchemaMixin, ProblemBaseSchema):
    """Схема для обновления проблемы.

    Назначение:
        Определяет структуру данных для обновления существующей проблемы.
    Параметры:
        name: Название проблемы (опционально).
        description: Описание проблемы (опционально).
        color: Цвет проблемы из перечисления ColorProblem (опционально).
        type: Тип проблемы из перечисления TypeProblem (опционально).
        status: Статус проблемы из перечисления StatusProblem (опционально).
        members: список участников, из связной таблицы, оформленных через схему (опционально).
    """

    name: str | None = None
    color: ColorProblem | None = None
    type: TypeProblem | None = None
    status: StatusProblem | None = None
