from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.problems.models.enums import ResultMeetingEnum, StatusMeeting
from src.problems.validators.meeting_validators import validate_date, validate_not_empty


class MeetingBaseSchema(BaseModel):
    """Базовая Pydantic-схема для встреч.

    Назначение:
        Определяет базовые поля и их типы для работы с данными встреч.
    Параметры:
        title: Название встречи.
        description: Описание встречи (опционально).
        date_meeting: Дата проведения встречи.
        status: Статус встречи.
        place: Место проведения встречи (опционально).
    """

    title: str
    description: Optional[str]
    date_meeting: date
    status: StatusMeeting
    place: Optional[str]
    # TODO Надо реализовать добавление файлов в встречу


class MeetingCreateSchema(BaseModel):
    """Pydantic-схема для создания встреч.

    Назначение:
        Используется для валидации данных при создании новой встречи.
    Параметры:
        problem_id: Идентификатор связанной проблемы.
        owner_id: Идентификатор создателя встречи.
        members: Список идентификаторов участников (опционально).
        id: Идентификатор встречи (временное значение).
    """
    title: str
    description: str | None
    date_meeting: date
    place: str

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


class MeetingUpdateSchema(BaseModel):
    """Pydantic-схема для обновления информации о встрече.

    Назначение:
        Используется для валидации данных при обновлении информации о встрече.
    Параметры:
        title: Название встречи (опционально).
        description: Описание встречи (опционально).
        date_meeting: Дата проведения встречи (опционально).
        status: Статус встречи (опционально).
        place: Место проведения встречи (опционально).
    """

    title: Optional[str]
    description: Optional[str]
    date_meeting: Optional[date]
    place: Optional[str]
    status: Optional[StatusMeeting]
    members: list[UUID] | None = []

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


class MemberResponseSchema(BaseModel):

    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(from_attributes=True)


class MeetingResponseSchema(BaseModel):
    """Pydantic-схема для данных о встрече из БД.

    Назначение:
        Используется для сериализации данных о встрече при получении из БД.
    Параметры:
        id: Идентификатор встречи.
        created_at: Дата и время создания записи.
        updated_at: Дата и время последнего обновления записи.
    """

    id: int
    title: str
    description: str | None
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
