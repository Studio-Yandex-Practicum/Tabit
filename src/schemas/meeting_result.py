from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from src.models import (
    MeetingResultEngagementEnum,
    MeetingResultEnum,
    MeetingResultSolutionEnum,
)

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

FeedbackStr = Annotated[str, StringConstraints(max_length=1000)]
PlaceStr = Annotated[str, StringConstraints(min_length=1)]

class MeetingResultBaseSchema(BaseModel):
    """Базовая схема для результатов встреч."""
    meeting_result: Optional[MeetingResultEnum] = Field(
        None, title="Результат встречи"
    )
    participant_engagement: Optional[MeetingResultEngagementEnum] = Field(
        None, title="Участие в встрече"
    )
    problem_solution: Optional[MeetingResultSolutionEnum] = Field(
        None, title="Решение проблемы"
    )
    meeting_feedback: Optional[FeedbackStr] = Field(None, title="Отзыв о встрече")

    model_config = BASE_CONFIG

class MeetingResultCreateSchema(MeetingResultBaseSchema):
    """Схема для создания результатов встреч."""
    meeting_result: MeetingResultEnum
    participant_engagement: MeetingResultEngagementEnum
    problem_solution: MeetingResultSolutionEnum

    model_config = BASE_CONFIG

class MeetingResultSchema(BaseModel):
    """Схема для данных о встрече из связанной модели Meeting."""
    place: PlaceStr = Field(..., title="Место проведения встречи")
    date_meeting: date = Field(..., title="Дата проведения встречи")

    model_config = BASE_CONFIG

class MeetingResultResponseSchema(MeetingResultBaseSchema):
    """Схема для данных о результатах встречи из БД."""
    id: int
    owner_id: UUID
    meeting: MeetingResultSchema
    meeting_result: MeetingResultEnum
    participant_engagement: MeetingResultEngagementEnum
    problem_solution: MeetingResultSolutionEnum

    model_config = BASE_CONFIG

class MeetingResultUpdateSchema(MeetingResultBaseSchema):
    """Схема для обновления результатов встреч."""
    model_config = BASE_CONFIG