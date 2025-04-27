from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from src.models import MeetingStatus
from src.schemas.constants import Length, Title

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

TitleStr = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
OptionalTitleStr = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
DescriptionStr = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_DESCRIPTION, max_length=Length.MAX_DESCRIPTION_COMPANY)
]
PlaceStr = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
OptionalPlaceStr = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]

class MeetingBaseSchema(BaseModel):
    """Базовая Pydantic-схема для встреч."""
    description: DescriptionStr = Field(None, title=Title.MEETING_DESCRIPTION)

    # TODO: Надо реализовать добавление файлов в встречу

class MeetingCreateSchema(MeetingBaseSchema):
    """Pydantic-схема для создания встреч."""
    title: TitleStr = Field(..., title=Title.MEETING_TITLE)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)
    place: PlaceStr = Field(..., title=Title.MEETING_PLACE)

    model_config = BASE_CONFIG

class MeetingUpdateSchema(MeetingBaseSchema):
    """Pydantic-схема для обновления информации о встрече."""
    title: OptionalTitleStr = Field(None, title=Title.MEETING_TITLE)
    date_meeting: Optional[date] = Field(None, title=Title.MEETING_DATE)
    place: OptionalPlaceStr = Field(None, title=Title.MEETING_PLACE)
    status: Optional[MeetingStatus] = Field(None, title=Title.MEETING_STATUS)
    members: Optional[list[UUID]] = Field(default=[], title=Title.MEETING_MEMBERS)

    model_config = BASE_CONFIG

class MemberResponseSchema(BaseModel):
    """Схема участника Встречи."""
    member_id: UUID = Field(validation_alias='left_id', title=Title.MEETING_MEMBER_ID)

    model_config = ConfigDict(from_attributes=True)

class MeetingResponseSchema(MeetingBaseSchema):
    """Pydantic-схема для данных о встрече из БД."""
    id: int = Field(..., title=Title.ID)
    title: TitleStr = Field(..., title=Title.MEETING_TITLE)
    problem_id: int = Field(..., title=Title.MEETING_PROBLEM_ID)
    owner_id: UUID = Field(..., title=Title.MEETING_OWNER_ID)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)
    status: MeetingStatus = Field(..., title=Title.MEETING_STATUS)
    place: PlaceStr = Field(..., title=Title.MEETING_PLACE)
    members: list[MemberResponseSchema] = Field(..., title=Title.MEETING_MEMBERS)
    transfer_counter: int = Field(..., title=Title.MEETING_TRANSFER_COUNTER)
    created_at: datetime = Field(..., title=Title.MEETING_CREATED_AT)
    updated_at: datetime = Field(..., title=Title.MEETING_UPDATED_AT)

    model_config = ConfigDict(from_attributes=True)