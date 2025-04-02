from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.problems.models.enums import (
    ResultMeetingEngagementEnum,
    ResultMeetingEnum,
    ResultMeetingSolutionEnum,
    StatusMeeting,
)
from src.problems.validators.meeting_validators import validate_date, validate_not_empty


class MeetingBaseSchema(BaseModel):
    """
    Параметры:
        description: Описание встречи (опционально).
    """

    description: str | None = None
    # TODO: Надо реализовать добавление файлов в встречу

    model_config = ConfigDict(
        title='Схема для встреч', description='Определяет базовые полядля работы с данными встреч'
    )


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
    """
    Параметры:
        title: Название встречи.
        date_meeting: Дата проведения встречи.
        place: Место проведения встречи.
    """

    title: str
    date_meeting: date
    place: str

    model_config = ConfigDict(
        title='Схема для создания встреч',
        description='Используется для валидации данных при создании новой встречи',
    )


class MeetingUpdateSchema(MeetingSchemaMixin, MeetingBaseSchema):
    """
    Параметры:
        title: Название встречи (опционально).
        date_meeting: Дата проведения встречи (опционально).
        place: Место проведения встречи (опционально).
        status: Статус встречи (опционально).
        members: список участников, из связной таблицы, оформленных через схему (опционально).
    """

    title: str | None = None
    date_meeting: date | None = None
    place: str | None = None
    status: StatusMeeting | None = None
    members: list[UUID] | None = []

    model_config = ConfigDict(
        title='Схема для обновления информации о встрече',
        description='Используется для валидации данных при обновлении информации о встрече',
    )


class MemberResponseSchema(BaseModel):
    """
    Параметры:
        member_id: UUID участника Встречи.
    """

    member_id: UUID = Field(validation_alias='left_id')

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема участника Встречи',
        description='Определяет структуру данных для ответа с информацией о участнике Встречи',
    )


class MeetingResponseSchema(MeetingBaseSchema):
    """
    Параметры:
        id: Идентификатор встречи.
        title: Название встречи.
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

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема для данных о встрече из БД',
        description='Используется для сериализации данных о встрече при получении из БД',
    )


class ResultMeetingBaseSchema(BaseModel):
    """
    Параметры:
        meeting_result: Результат встречи.
        participant_engagement: Участие в встрече.
        problem_solution: Решение проблемы.
        meeting_feedback: Отзыв о встрече (опционально).
    """

    meeting_result: ResultMeetingEnum
    participant_engagement: ResultMeetingEngagementEnum
    problem_solution: ResultMeetingSolutionEnum
    meeting_feedback: Optional[str]

    model_config = ConfigDict(
        title='Базовая схема для результатов встреч',
        description='Определяет базовые поля и их типы для работы с результатами встреч',
    )


class ResultMeetingCreateSchema(ResultMeetingBaseSchema):
    """
    Используется для валидации данных при создании результатов встречи.
    """

    model_config = ConfigDict(
        extra='forbid',
        str_min_length=1,
        title='Схема для создания результатов встреч',
        description='Используется для валидации данных при создании результатов встречи',
    )


class ResultMeetingSchema(BaseModel):
    """
    Параметры:
        place: Место проведения встречи.
        date_meeting: Дата проведения встречи.
    """

    place: str
    date_meeting: date

    model_config = ConfigDict(
        extra='forbid',
        str_min_length=1,
        title='Схема результатов встреч',
        description='Используется для сериализации данных о результатах встречи при получении из БД.',
    )


class ResultMeetingResponseSchema(ResultMeetingBaseSchema):
    """
    Параметры:
        id: Идентификатор результата.
        meeting_id: Идентификатор связанной встречи.
        owner_id: Идентификатор создателя результата.
        meeting: Поля из модели Meeting.
    """

    id: int
    owner_id: UUID
    meeting: ResultMeetingSchema

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема для данных о результатах встречи из БД',
        description=(
            'Используется для сериализации данных о результатах встречи при получении из БД'
        ),
    )


class ResultMeetingUpdateSchema(BaseModel):
    """
    Параметры:
        meeting_result: Результат встречи (опционально).
        participant_engagement: Участие в встрече (опционально).
        problem_solution: Решение проблемы (опционально).
        meeting_feedback: Отзыв о встрече (опционально).
    """

    meeting_result: Optional[ResultMeetingEnum] = None
    participant_engagement: Optional[ResultMeetingEngagementEnum] = None
    problem_solution: Optional[ResultMeetingSolutionEnum] = None
    meeting_feedback: Optional[str] = None

    model_config = ConfigDict(
        extra='forbid',
        title='Схема для обновления результатов встреч',
        description='Используется для валидации данных при обновлении результатов встречи'
    )

