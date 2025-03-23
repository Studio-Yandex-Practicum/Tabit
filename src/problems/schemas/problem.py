from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator, ConfigDict, Field

from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem
from src.problems.validators.problem_validators import validate_not_empty


class ProblemBaseSchema(BaseModel):
    """Базовая схема Проблеммы.

    Назначение:
        Определяет базовую структуру данных для проблемы.
    Параметры:
        name: Название проблемы.
        description: Описание проблемы (опционально).
        color: Цвет проблемы из перечисления ColorProblem.
        type: Тип проблемы из перечисления TypeProblem.
        status: Статус проблемы из перечисления StatusProblem.
        owner_id: UUID владельца проблемы.
        company_slug: Слаг компании, с которой связана проблема.
    """

    description: str | None = None

    # TODO Надо реализовать добавление файлов в проблему


class MemberResponseSchema(BaseModel):

    status: bool | None
    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class ProblemResponseSchema(BaseModel):
    """Схема Проблемы для ответа.

    Назначение:
        Определяет структуру данных для ответа с информацией о проблеме.
    Параметры:
        id: Уникальный идентификатор проблемы.
        created_at: Время создания проблемы.
        updated_at: Время последнего обновления проблемы.
    """

    id: int
    name: str
    description: str | None
    color: ColorProblem
    type: TypeProblem
    status: StatusProblem
    owner_id: UUID
    company_id: int
    created_at: datetime
    updated_at: datetime
    members: list[MemberResponseSchema]

    model_config = ConfigDict(from_attributes=True)


class ProblemSchemaMixin:

    members: list[UUID] | None = []

    model_config = ConfigDict(extra='forbid')

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        """Проверка, что название проблемы не пустое."""
        return validate_not_empty(value)


class ProblemCreateSchema(ProblemSchemaMixin, ProblemBaseSchema):
    """Схема для создания проблемы.

    Назначение:
        Определяет структуру данных для создания новой проблемы.
    """

    name: str
    color: ColorProblem
    type: TypeProblem


class ProblemUpdateSchema(ProblemSchemaMixin, ProblemBaseSchema):
    """Схема для обновления проблемы.

    Назначение:
        Определяет структуру данных для обновления существующей проблемы.
    Параметры:
        name: Новое название проблемы (опционально).
        description: Новое описание проблемы (опционально).
        color: Новый цвет проблемы (опционально).
        type: Новый тип проблемы (опционально).
        status: Новый статус проблемы (опционально).
        owner_id: Новый владелец проблемы (опционально).
    """

    name: str | None = None
    color: ColorProblem | None = None
    type: TypeProblem | None = None
    status: StatusProblem | None = None
