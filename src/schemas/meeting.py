from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.models import MeetingStatus


class MeetingBaseSchema(BaseModel):
    """Базовая схема встречи.

    Определяет базовые поля встречи.
    Поля:
        description: Описание встречи (опционально).
    """
    description: str | None = None
    # TODO: Реализовать добавление файлов в встречу

    model_config = ConfigDict(extra='forbid')


class MemberResponseSchema(BaseModel):
    """Схема участника встречи.

    Определяет данные участника для ответа.
    Поля:
        member_id: UUID участника.
    """
    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class MeetingResponseSchema(MeetingBaseSchema):
    """Схема встречи для ответа.

    Определяет данные встречи из БД.
    Поля:
        id: Идентификатор встречи.
        title: Название встречи.
        problem_id: ID проблемы.
        owner_id: UUID создателя.
        date_meeting: Дата проведения.
        status: Статус встречи.
        place: Место проведения.
        members: Список участников.
        transfer_counter: Количество переносов даты.
        created_at: Время создания.
        updated_at: Время обновления.
    """
    id: int
    title: str
    problem_id: int
    owner_id: UUID
    date_meeting: date
    status: MeetingStatus
    place: str
    members: list[MemberResponseSchema]
    transfer_counter: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingCreateSchema(MeetingBaseSchema):
    """Схема для создания встречи.

    Определяет данные для создания встречи.
    Поля:
        title: Название (не пустое, без пробелов).
        date_meeting: Дата проведения (в будущем).
        place: Место проведения.
    """
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    date_meeting: Annotated[
        date,
        Field(..., ge=date.today())
    ]
    place: str

    model_config = ConfigDict(extra='forbid')


class MeetingUpdateSchema(MeetingBaseSchema):
    """Схема для обновления встречи.

    Определяет данные для обновления встречи.
    Поля:
        title: Название (опционально, не пустое, без пробелов).
        date_meeting: Дата проведения (опционально, в будущем).
        place: Место проведения (опционально).
        status: Статус встречи (опционально).
        members: Список UUID участников (опционально).
    """
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = None
    date_meeting: Annotated[
        date,
        Field(None, ge=date.today())
    ] | None = None
    place: str | None = None
    status: MeetingStatus | None = None
    members: list[UUID] | None = []

    model_config = ConfigDict(extra='forbid')