from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models import (
    MeetingResultEngagementEnum,
    MeetingResultEnum,
    MeetingResultSolutionEnum,
)
from src.schemas.annotations import FeedbackField, PlaceField
from src.schemas.constants import Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class MeetingResultBaseSchema(BaseModel):
    """
    Базовая схема для результатов встреч.

    Определяет общие поля для схем результатов встреч.

    Атрибуты:
        meeting_result (Optional[MeetingResultEnum]): Результат встречи.
        participant_engagement (Optional[MeetingResultEngagementEnum]): Уровень
            вовлеченности участников.
        problem_solution (Optional[MeetingResultSolutionEnum]): Решение проблемы.
        meeting_feedback (Optional[str]): Обратная связь по встрече.
    """

    meeting_result: Optional[MeetingResultEnum] = Field(None, title=Title.MEETING_RESULT)
    participant_engagement: Optional[MeetingResultEngagementEnum] = Field(
        None, title=Title.PARTICIPANT_ENGAGEMENT
    )
    problem_solution: Optional[MeetingResultSolutionEnum] = Field(
        None, title=Title.PROBLEM_SOLUTION
    )
    meeting_feedback: Optional[FeedbackField] = Field(None, title=Title.MEETING_FEEDBACK)

    model_config = BASE_CONFIG


class MeetingResultCreateSchema(MeetingResultBaseSchema):
    """
    Схема для создания результатов встреч.

    Используется для добавления новых результатов встречи через API.

    Атрибуты:
        meeting_result (MeetingResultEnum): Результат встречи.
        participant_engagement (MeetingResultEngagementEnum): Уровень
            вовлеченности участников.
        problem_solution (MeetingResultSolutionEnum): Решение проблемы.
        meeting_feedback (Optional[str]): Обратная связь по встрече.
    """

    meeting_result: MeetingResultEnum = Field(..., title=Title.MEETING_RESULT)
    participant_engagement: MeetingResultEngagementEnum = Field(
        ..., title=Title.PARTICIPANT_ENGAGEMENT
    )
    problem_solution: MeetingResultSolutionEnum = Field(..., title=Title.PROBLEM_SOLUTION)

    model_config = BASE_CONFIG


class MeetingResultSchema(BaseModel):
    """
    Схема для данных о встрече из связанной модели Meeting.

    Используется для представления данных о встрече.

    Атрибуты:
        place (str): Место проведения встречи.
        date_meeting (date): Дата проведения встречи.
    """

    place: PlaceField = Field(..., title=Title.MEETING_PLACE)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)

    model_config = BASE_CONFIG


class MeetingResultResponseSchema(MeetingResultBaseSchema):
    """
    Схема для данных о результатах встречи из БД.

    Используется для возврата данных о результатах встречи через API.

    Атрибуты:
        id (int): Идентификатор результата встречи.
        owner_id (UUID): Идентификатор владельца результата.
        meeting (MeetingResultSchema): Данные о встрече.
        meeting_result (MeetingResultEnum): Результат встречи.
        participant_engagement (MeetingResultEngagementEnum): Уровень
            вовлеченности участников.
        problem_solution (MeetingResultSolutionEnum): Решение проблемы.
        meeting_feedback (Optional[str]): Обратная связь по встрече.
    """

    id: int
    owner_id: UUID
    meeting: MeetingResultSchema
    meeting_result: MeetingResultEnum = Field(..., title=Title.MEETING_RESULT)
    participant_engagement: MeetingResultEngagementEnum = Field(
        ..., title=Title.PARTICIPANT_ENGAGEMENT
    )
    problem_solution: MeetingResultSolutionEnum = Field(..., title=Title.PROBLEM_SOLUTION)

    model_config = BASE_CONFIG


class MeetingResultUpdateSchema(MeetingResultBaseSchema):
    """
    Схема для обновления результатов встреч.

    Используется для изменения данных о результатах встречи через API.

    Атрибуты:
        meeting_result (Optional[MeetingResultEnum]): Результат встречи.
        participant_engagement (Optional[MeetingResultEngagementEnum]): Уровень
            вовлеченности участников.
        problem_solution (Optional[MeetingResultSolutionEnum]): Решение проблемы.
        meeting_feedback (Optional[str]): Обратная связь по встрече.
    """

    model_config = BASE_CONFIG
