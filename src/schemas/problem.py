from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models import ProblemColor, ProblemStatus, ProblemType
from src.schemas.annotations import DescriptionField, NameField, OptionalNameField
from src.schemas.constants import TitleConstants


class ProblemBaseSchema(BaseModel):
    """
    Базовая схема проблемы.

    Определяет общие поля для схем проблем.

    Атрибуты:
        description (Optional[str]): Описание проблемы.
    """

    description: DescriptionField = Field(None, title=TitleConstants.PROBLEM_DESCRIPTION)
    # TODO: Реализовать добавление файлов в проблему

    model_config = ConfigDict(extra='forbid')


class MemberResponseSchema(BaseModel):
    """
    Схема участника проблемы.

    Используется для представления данных об участнике проблемы в ответах API.

    Атрибуты:
        status (Optional[bool]): Статус участия в решении проблемы.
        member_id (UUID): Идентификатор участника.
    """

    status: bool | None = Field(None, title=TitleConstants.PROBLEM_MEMBER_STATUS)
    member_id: UUID = Field(validation_alias='left_id', title=TitleConstants.PROBLEM_MEMBER_ID)

    model_config = ConfigDict(from_attributes=True)


class ProblemResponseSchema(ProblemBaseSchema):
    """
    Схема проблемы для ответа.

    Используется для возврата данных о проблеме через API.

    Атрибуты:
        id (int): Уникальный идентификатор проблемы.
        name (str): Название проблемы.
        color (ProblemColor): Цвет проблемы.
        type (ProblemType): Тип проблемы.
        status (ProblemStatus): Статус проблемы.
        owner_id (UUID): Идентификатор владельца проблемы.
        company_id (int): Идентификатор компании.
        members (list[MemberResponseSchema]): Список участников проблемы.
        created_at (datetime): Время создания проблемы.
        updated_at (datetime): Время последнего обновления проблемы.
        description (Optional[str]): Описание проблемы.
    """

    id: int = Field(..., title=TitleConstants.PROBLEM_ID)
    name: str = Field(..., title=TitleConstants.PROBLEM_NAME)
    color: ProblemColor = Field(..., title=TitleConstants.PROBLEM_COLOR)
    type: ProblemType = Field(..., title=TitleConstants.PROBLEM_TYPE)
    status: ProblemStatus = Field(..., title=TitleConstants.PROBLEM_STATUS)
    owner_id: UUID = Field(..., title=TitleConstants.PROBLEM_OWNER_ID)
    company_id: int = Field(..., title=TitleConstants.PROBLEM_COMPANY_ID)
    members: list[MemberResponseSchema] = Field(..., title=TitleConstants.PROBLEM_MEMBERS)
    created_at: datetime = Field(..., title=TitleConstants.PROBLEM_CREATED_AT)
    updated_at: datetime = Field(..., title=TitleConstants.PROBLEM_UPDATED_AT)

    model_config = ConfigDict(from_attributes=True)


class ProblemCreateSchema(ProblemBaseSchema):
    """
    Схема для создания проблемы.

    Используется для добавления новой проблемы через API.

    Атрибуты:
        name (str): Название проблемы.
        color (ProblemColor): Цвет проблемы.
        type (ProblemType): Тип проблемы.
        members (Optional[list[UUID]]): Список идентификаторов участников.
        description (Optional[str]): Описание проблемы.
    """

    name: NameField = Field(..., title=TitleConstants.PROBLEM_NAME)
    color: ProblemColor = Field(..., title=TitleConstants.PROBLEM_COLOR)
    type: ProblemType = Field(..., title=TitleConstants.PROBLEM_TYPE)
    members: list[UUID] | None = Field(default=[], title=TitleConstants.PROBLEM_MEMBERS)

    model_config = ConfigDict(extra='forbid')


class ProblemUpdateSchema(ProblemBaseSchema):
    """
    Схема для обновления проблемы.

    Используется для изменения данных проблемы через API.

    Атрибуты:
        name (Optional[str]): Название проблемы.
        color (Optional[ProblemColor]): Цвет проблемы.
        type (Optional[ProblemType]): Тип проблемы.
        status (Optional[ProblemStatus]): Статус проблемы.
        members (Optional[list[UUID]]): Список идентификаторов участников.
        description (Optional[str]): Описание проблемы.
    """

    name: OptionalNameField = Field(None, title=TitleConstants.PROBLEM_NAME)
    color: ProblemColor | None = Field(None, title=TitleConstants.PROBLEM_COLOR)
    type: ProblemType | None = Field(None, title=TitleConstants.PROBLEM_TYPE)
    status: ProblemStatus | None = Field(None, title=TitleConstants.PROBLEM_STATUS)
    members: list[UUID] | None = Field(None, title=TitleConstants.PROBLEM_MEMBERS)

    model_config = ConfigDict(extra='forbid')
