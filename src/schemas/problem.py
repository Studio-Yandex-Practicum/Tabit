from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.models import ProblemColor, ProblemStatus, ProblemType


class ProblemBaseSchema(BaseModel):
    """Базовая схема проблемы.

    Определяет базовую структуру данных для проблемы.
    Поля:
        description: Описание проблемы (опционально).
    """
    description: str | None = None
    # TODO: Реализовать добавление файлов в проблему

    model_config = ConfigDict(extra='forbid')


class MemberResponseSchema(BaseModel):
    """Схема участника проблемы.

    Определяет данные участника для ответа.
    Поля:
        status: Статус участия в решении проблемы.
        member_id: UUID участника.
    """
    status: bool | None
    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class ProblemResponseSchema(ProblemBaseSchema):
    """Схема проблемы для ответа.

    Определяет данные проблемы для ответа.
    Поля:
        id: Уникальный идентификатор.
        name: Название проблемы.
        color: Цвет проблемы.
        type: Тип проблемы.
        status: Статус проблемы.
        owner_id: UUID владельца.
        company_id: ID компании.
        members: Список участников.
        created_at: Время создания.
        updated_at: Время обновления.
    """
    id: int
    name: str
    color: ProblemColor
    type: ProblemType
    status: ProblemStatus
    owner_id: UUID
    company_id: int
    members: list[MemberResponseSchema]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProblemCreateSchema(ProblemBaseSchema):
    """Схема для создания проблемы.

    Определяет данные для создания проблемы.
    Поля:
        name: Название (не пустое, без пробелов).
        color: Цвет проблемы.
        type: Тип проблемы.
        members: Список UUID участников (опционально).
    """
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    color: ProblemColor
    type: ProblemType
    members: list[UUID] | None = []

    model_config = ConfigDict(extra='forbid')


class ProblemUpdateSchema(ProblemBaseSchema):
    """Схема для обновления проблемы.

    Определяет данные для обновления проблемы.
    Поля:
        name: Название (опционально, не пустое, без пробелов).
        color: Цвет (опционально).
        type: Тип (опционально).
        status: Статус (опционально).
        members: Список UUID участников (опционально).
    """
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = None
    color: ProblemColor | None = None
    type: ProblemType | None = None
    status: ProblemStatus | None = None
    members: list[UUID] | None = None

    model_config = ConfigDict(extra='forbid')