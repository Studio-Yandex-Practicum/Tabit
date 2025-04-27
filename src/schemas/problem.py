from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.models import ProblemColor, ProblemStatus, ProblemType
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


class ProblemBaseSchema(BaseModel):
    """Базовая схема проблемы.

    Определяет базовую структуру данных для проблемы.
    Поля:
        description: Описание проблемы (опционально).
    """

    description: DescriptionStr = Field(None, title=Title.PROBLEM_DESCRIPTION)
    # TODO: Реализовать добавление файлов в проблему

    model_config = ConfigDict(extra='forbid')


class MemberResponseSchema(BaseModel):
    """Схема участника проблемы.

    Определяет данные участника для ответа.
    Поля:
        status: Статус участия в решении проблемы.
        member_id: UUID участника.
    """

    status: bool | None = Field(None, title=Title.PROBLEM_MEMBER_STATUS)
    member_id: UUID = Field(validation_alias='left_id', title=Title.PROBLEM_MEMBER_ID)

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

    id: int = Field(..., title=Title.ID)
    name: str = Field(..., title=Title.PROBLEM_NAME)
    color: ProblemColor = Field(..., title=Title.PROBLEM_COLOR)
    type: ProblemType = Field(..., title=Title.PROBLEM_TYPE)
    status: ProblemStatus = Field(..., title=Title.PROBLEM_STATUS)
    owner_id: UUID = Field(..., title=Title.PROBLEM_OWNER_ID)
    company_id: int = Field(..., title=Title.PROBLEM_COMPANY_ID)
    members: list[MemberResponseSchema] = Field(..., title=Title.PROBLEM_MEMBERS)
    created_at: datetime = Field(..., title=Title.PROBLEM_CREATED_AT)
    updated_at: datetime = Field(..., title=Title.PROBLEM_UPDATED_AT)

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

    name: NameStr = Field(..., title=Title.PROBLEM_NAME)
    color: ProblemColor = Field(..., title=Title.PROBLEM_COLOR)
    type: ProblemType = Field(..., title=Title.PROBLEM_TYPE)
    members: list[UUID] | None = Field(default=[], title=Title.PROBLEM_MEMBERS)

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

    name: OptionalNameStr = Field(None, title=Title.PROBLEM_NAME)
    color: ProblemColor | None = Field(None, title=Title.PROBLEM_COLOR)
    type: ProblemType | None = Field(None, title=Title.PROBLEM_TYPE)
    status: ProblemStatus | None = Field(None, title=Title.PROBLEM_STATUS)
    members: list[UUID] | None = Field(None, title=Title.PROBLEM_MEMBERS)

    model_config = ConfigDict(extra='forbid')
