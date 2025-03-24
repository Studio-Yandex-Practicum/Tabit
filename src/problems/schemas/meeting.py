from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.problems.models.enums import ResultMeetingEnum, StatusMeeting
from src.problems.validators.meeting_validators import validate_date, validate_not_empty


class MeetingBaseSchema(BaseModel):
    """Базовая Pydantic-схема для встреч.

    Назначение:
        Определяет базовые поля и их типы для работы с данными встреч.
    Параметры:
        description: Описание встречи (опционально).
    """

    description: str | None
    # TODO Надо реализовать добавление файлов в встречу


class MeetingSchemaMixin:
    """
    Миксин для схем Встреч, с валидаторами.
    """

    model_config = ConfigDict(extra='forbid', str_min_length=1)

    @field_validator('title')
    @classmethod
    def validate_title_not_empty(cls, value: str) -> str:
        """Проверка, что название проблемы не пустое."""
        return validate_not_empty(value)

    @field_validator('date_meeting')
    @classmethod
    def validate_date_meeting(cls, value: date) -> date:
        """Проверка, что дата не может быть меньше текущей."""
        return validate_date(value)


class MeetingCreateSchema(MeetingSchemaMixin, MeetingBaseSchema):
    """Pydantic-схема для создания встреч.

    Назначение:
        Используется для валидации данных при создании новой встречи.
    Параметры:
        title: Название встречи.
        description: Описание встречи (опционально).
        date_meeting: Дата проведения встречи.
        place: Место проведения встречи.
    """

    title: str
    date_meeting: date
    place: str


class MeetingUpdateSchema(MeetingSchemaMixin, MeetingBaseSchema):
    """Pydantic-схема для обновления информации о встрече.

    Назначение:
        Используется для валидации данных при обновлении информации о встрече.
    Параметры:
        title: Название встречи (опционально).
        description: Описание встречи (опционально).
        date_meeting: Дата проведения встречи (опционально).
        place: Место проведения встречи (опционально).
        status: Статус встречи (опционально).
        members: список участников, из связной таблицы, оформленных через схему (опционально).
    """

    title: str | None
    date_meeting: date | None
    place: str | None
    status: StatusMeeting | None
    members: list[UUID] | None = []


class MemberResponseSchema(BaseModel):
    """Схема участника Встречи.

    Назначение:
        Определяет структуру данных для ответа с информацией о участнике Встречи.
    Параметры:
        member_id: UUID участника Встречи.
    """

    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class MeetingResponseSchema(MeetingBaseSchema):
    """Pydantic-схема для данных о встрече из БД.

    Назначение:
        Используется для сериализации данных о встрече при получении из БД.
    Параметры:
        id: Идентификатор встречи.
        title: Название встречи.
        description: Описание встречи (опционально).
        problem_id: Идентификационный номер проблемы по которой назначена встреча.
        owner_id: Идентификационный номер пользователя, который создал встречу.
        date_meeting: Дата проведения встречи.
        status: Статус встречи.
        place: Место проведения встречи.
        members: список участников, из связной таблицы, оформленных через схему.
        transfer_counter: количество переносов даты проведения встречи.
        created_at: Дата и время создания записи.
        updated_at: Дата и время последнего обновления записи.
    """

    id: int
    title: str
    problem_id: int
    owner_id: UUID
    date_meeting: date
    status: StatusMeeting
    place: str
    members: list[MemberResponseSchema]
    transfer_counter: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResultMeetingBaseSchema(BaseModel):
    """Базовая Pydantic-схема для результатов встреч.

    Назначение:
        Определяет базовые поля и их типы для работы с результатами встреч.
    Параметры:
        meeting_result: Результат встречи.
        participant_engagement: Участие в встрече.
        problem_solution: Решение проблемы.
        meeting_feedback: Отзыв о встрече (опционально).
    """

    meeting_result: ResultMeetingEnum
    participant_engagement: bool
    problem_solution: bool
    meeting_feedback: Optional[str]


class ResultMeetingCreateSchema(ResultMeetingBaseSchema):
    """Pydantic-схема для создания результатов встреч.

    Назначение:
        Используется для валидации данных при создании результатов встречи.
    Параметры:
        meeting_id: Идентификатор связанной встречи.
        owner_id: Идентификатор создателя результата.
    """

    meeting_id: int
    owner_id: UUID

    model_config = ConfigDict(extra='forbid', str_min_length=1)


class ResultMeetingInDB(ResultMeetingBaseSchema):
    """Pydantic-схема для данных о результатах встречи из БД.

    Назначение:
        Используется для сериализации данных о результатах встречи при получении из БД.
    Параметры:
        id: Идентификатор результата.
        meeting_id: Идентификатор связанной встречи.
        owner_id: Идентификатор создателя результата.
    """

    id: int
    meeting_id: int
    owner_id: UUID

    model_config = ConfigDict(from_attributes=True)
