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
from src.schemas.constants import Length, Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)

FeedbackStr = Annotated[str, StringConstraints(max_length=Length.MAX_FEEDBACK_QUESTION_LENGTH)]
PlaceStr = Annotated[str, StringConstraints(min_length=Length.MIN_NAME)]


class MeetingResultBaseSchema(BaseModel):
    """Базовая схема для результатов встреч."""

    meeting_result: Optional[MeetingResultEnum] = Field(None, title=Title.MEETING_RESULT)
    participant_engagement: Optional[MeetingResultEngagementEnum] = Field(
        None, title=Title.PARTICIPANT_ENGAGEMENT
    )
    problem_solution: Optional[MeetingResultSolutionEnum] = Field(
        None, title=Title.PROBLEM_SOLUTION
    )
    meeting_feedback: Optional[FeedbackStr] = Field(None, title=Title.MEETING_FEEDBACK)

    model_config = BASE_CONFIG


class MeetingResultCreateSchema(MeetingResultBaseSchema):
    """Схема для создания результатов встреч."""

    meeting_result: MeetingResultEnum = Field(..., title=Title.MEETING_RESULT)
    participant_engagement: MeetingResultEngagementEnum = Field(
        ..., title=Title.PARTICIPANT_ENGAGEMENT
    )
    problem_solution: MeetingResultSolutionEnum = Field(..., title=Title.PROBLEM_SOLUTION)

    model_config = BASE_CONFIG


class MeetingResultSchema(BaseModel):
    """Схема для данных о встрече из связанной модели Meeting."""

    place: PlaceStr = Field(..., title=Title.MEETING_PLACE)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)

    model_config = BASE_CONFIG


class MeetingResultResponseSchema(MeetingResultBaseSchema):
    """Схема для данных о результатах встречи из БД."""

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
    """Схема для обновления результатов встреч."""

    model_config = BASE_CONFIG
