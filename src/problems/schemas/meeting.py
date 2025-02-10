from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from src.problems.models.enums import StatusMeeting, ResultMeetingEnum


class MeetingBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для встреч.
    """

    title: str
    description: Optional[str]
    date_meeting: date
    status: StatusMeeting
    place: Optional[str]
    # file_id: Optional[int]


class MeetingCreateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для создания встреч.
    """

    problem_id: int
    owner_id: UUID
    members: Optional[List[UUID]] = None

    model_config = ConfigDict(extra='forbid', str_min_length=1)


class MeetingUpdateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для обновления информации о встрече.
    """

    title: Optional[str]
    description: Optional[str]
    date_meeting: Optional[date]
    status: Optional[StatusMeeting]
    place: Optional[str]

    @field_validator('title', 'description')
    def value_cant_be_null(cls, value: str):
        if not value:
            raise ValueError(f'{cls} не может быть пустым.')
        return value

    @field_validator('date_meeting')
    def date_meeting_validation(value: date) -> date:
        if value < date.today():
            raise ValueError(f'Дата не может быть {date.today()}')
        return value

    model_config = ConfigDict(extra='forbid', str_min_length=1)


class MeetingInDB(MeetingBaseSchema):
    """
    Pydantic-схема для данных о встрече из БД.
    """

    id: int
    file: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResultMeetingBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для результатов встреч.
    """

    meeting_result: ResultMeetingEnum
    participant_engagement: bool
    problem_solution: bool
    meeting_feedback: Optional[str]


class ResultMeetingCreateSchema(ResultMeetingBaseSchema):
    """
    Pydantic-схема для создания результатов встреч.
    """

    meeting_id: int
    owner_id: UUID

    model_config = ConfigDict(extra='forbid', str_min_length=1)


class ResultMeetingInDB(ResultMeetingBaseSchema):
    """
    Pydantic-схема для данных о результатах встречи из БД.
    """

    id: int
    meeting_id: int
    owner_id: UUID

    model_config = ConfigDict(from_attributes=True)
