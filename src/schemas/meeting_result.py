from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models import (
    MeetingResultEngagementEnum,
    MeetingResultEnum,
    MeetingResultSolutionEnum,
)


class MeetingResultBaseSchema(BaseModel):
    """Базовая Pydantic-схема для результатов встреч.

    Назначение:
        Определяет базовые поля и их типы для работы с результатами встреч.
    Параметры:
        meeting_result: Результат встречи.
        participant_engagement: Участие в встрече.
        problem_solution: Решение проблемы.
        meeting_feedback: Отзыв о встрече (опционально).
    """

    meeting_result: MeetingResultEnum
    participant_engagement: MeetingResultEngagementEnum
    problem_solution: MeetingResultSolutionEnum
    meeting_feedback: Optional[str]


class MeetingResultCreateSchema(MeetingResultBaseSchema):
    """Pydantic-схема для создания результатов встреч.

    Назначение:
        Используется для валидации данных при создании результатов встречи.
    """

    model_config = ConfigDict(extra='forbid', str_min_length=1)


class MeetingResultSchema(BaseModel):
    """Pydantic-схема для данных о результатах встречи из БД из связанной модели Meeting.

    Назначение:
        Используется для сериализации данных о результатах встречи при получении из БД.
    Параметры:
        place: Место проведения встречи.
        date_meeting: Дата проведения встречи.
    """

    place: str
    date_meeting: date

    model_config = ConfigDict(from_attributes=True)


class MeetingResultResponseSchema(MeetingResultBaseSchema):
    """Pydantic-схема для данных о результатах встречи из БД.

    Назначение:
        Используется для сериализации данных о результатах встречи при получении из БД.
    Параметры:
        id: Идентификатор результата.
        meeting_id: Идентификатор связанной встречи.
        owner_id: Идентификатор создателя результата.
        meeting: Поля из модели Meeting.
    """

    id: int
    owner_id: UUID
    meeting: MeetingResultSchema

    model_config = ConfigDict(from_attributes=True)


class MeetingResultUpdateSchema(BaseModel):
    """Pydantic-схема для обновления результатов встреч.

    Назначение:
        Используется для валидации данных при обновлении результатов встречи.
    Параметры:
        meeting_result: Результат встречи (опционально).
        participant_engagement: Участие в встрече (опционально).
        problem_solution: Решение проблемы (опционально).
        meeting_feedback: Отзыв о встрече (опционально).
    """

    meeting_result: Optional[MeetingResultEnum] = None
    participant_engagement: Optional[MeetingResultEngagementEnum] = None
    problem_solution: Optional[MeetingResultSolutionEnum] = None
    meeting_feedback: Optional[str] = None

    model_config = ConfigDict(extra='forbid')
