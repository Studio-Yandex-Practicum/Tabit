from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models import MeetingStatus
from src.schemas.constants import Title
from src.schemas.types import (
    DescriptionField,
    OptionalPlaceField,
    OptionalTitleField,
    PlaceField,
    TitleField,
)

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)



class MeetingBaseSchema(BaseModel):
    """Базовая Pydantic-схема для встреч."""
    description: DescriptionField = Field(None, title=Title.MEETING_DESCRIPTION)

    # TODO: Надо реализовать добавление файлов в встречу

class MeetingCreateSchema(MeetingBaseSchema):
    """Pydantic-схема для создания встреч."""
    title: TitleField = Field(..., title=Title.MEETING_TITLE)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)
    place: PlaceField = Field(..., title=Title.MEETING_PLACE)

    model_config = BASE_CONFIG

class MeetingUpdateSchema(MeetingBaseSchema):
    """Pydantic-схема для обновления информации о встрече."""
    title: OptionalTitleField = Field(None, title=Title.MEETING_TITLE)
    date_meeting: Optional[date] = Field(None, title=Title.MEETING_DATE)
    place: OptionalPlaceField = Field(None, title=Title.MEETING_PLACE)
    status: Optional[MeetingStatus] = Field(None, title=Title.MEETING_STATUS)
    members: Optional[list[UUID]] = Field(default=[], title=Title.MEETING_MEMBERS)

    model_config = BASE_CONFIG

class MemberResponseSchema(BaseModel):
    """Схема участника Встречи."""
    member_id: UUID = Field(validation_alias='left_id', title=Title.MEETING_MEMBER_ID)

    model_config = ConfigDict(from_attributes=True)

class MeetingResponseSchema(MeetingBaseSchema):
    """Pydantic-схема для данных о встрече из БД."""
    id: int = Field(..., title=Title.MEETING_ID)
    title: TitleField = Field(..., title=Title.MEETING_TITLE)
    problem_id: int = Field(..., title=Title.MEETING_PROBLEM_ID)
    owner_id: UUID = Field(..., title=Title.MEETING_OWNER_ID)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)
    status: MeetingStatus = Field(..., title=Title.MEETING_STATUS)
    place: PlaceField = Field(..., title=Title.MEETING_PLACE)
    members: list[MemberResponseSchema] = Field(..., title=Title.MEETING_MEMBERS)
    transfer_counter: int = Field(..., title=Title.MEETING_TRANSFER_COUNTER)
    created_at: datetime = Field(..., title=Title.MEETING_CREATED_AT)
    updated_at: datetime = Field(..., title=Title.MEETING_UPDATED_AT)

    model_config = ConfigDict(from_attributes=True)