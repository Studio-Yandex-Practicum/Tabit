from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models import MeetingStatus
from src.schemas.annotations import (
    DescriptionField,
    OptionalPlaceField,
    OptionalTitleField,
    PlaceField,
    TitleField,
)
from src.schemas.constants import Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class MeetingBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для встреч.

    Определяет общие поля для схем встреч.

    Атрибуты:
        description (Optional[str]): Описание встречи.
    """

    description: DescriptionField = Field(None, title=Title.MEETING_DESCRIPTION)

    # TODO: Надо реализовать добавление файлов в встречу


class MeetingCreateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для создания встреч.

    Используется для добавления новой встречи через API.

    Атрибуты:
        title (str): Название встречи.
        date_meeting (date): Дата проведения встречи.
        place (str): Место проведения встречи.
        description (Optional[str]): Описание встречи.
    """

    title: TitleField = Field(..., title=Title.MEETING_TITLE)
    date_meeting: date = Field(..., title=Title.MEETING_DATE)
    place: PlaceField = Field(..., title=Title.MEETING_PLACE)

    model_config = BASE_CONFIG


class MeetingUpdateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для обновления информации о встрече.

    Используется для изменения данных о встрече через API.

    Атрибуты:
        title (Optional[str]): Название встречи.
        date_meeting (Optional[date]): Дата проведения встречи.
        place (Optional[str]): Место проведения встречи.
        status (Optional[MeetingStatus]): Статус встречи.
        members (Optional[list[UUID]]): Список идентификаторов участников встречи.
        description (Optional[str]): Описание встречи.
    """

    title: OptionalTitleField = Field(None, title=Title.MEETING_TITLE)
    date_meeting: Optional[date] = Field(None, title=Title.MEETING_DATE)
    place: OptionalPlaceField = Field(None, title=Title.MEETING_PLACE)
    status: Optional[MeetingStatus] = Field(None, title=Title.MEETING_STATUS)
    members: Optional[list[UUID]] = Field(default=[], title=Title.MEETING_MEMBERS)

    model_config = BASE_CONFIG


class MemberResponseSchema(BaseModel):
    """
    Схема участника встречи.

    Используется для представления данных об участнике встречи.

    Атрибуты:
        member_id (UUID): Идентификатор участника встречи.
    """

    member_id: UUID = Field(validation_alias='left_id', title=Title.MEETING_MEMBER_ID)

    model_config = ConfigDict(from_attributes=True)


class MeetingResponseSchema(MeetingBaseSchema):
    """
    Pydantic-схема для данных о встрече из БД.

    Используется для возврата данных о встрече через API.

    Атрибуты:
        id (int): Идентификатор встречи.
        title (str): Название встречи.
        problem_id (int): Идентификатор связанной проблемы.
        owner_id (UUID): Идентификатор владельца встречи.
        date_meeting (date): Дата проведения встречи.
        status (MeetingStatus): Статус встречи.
        place (str): Место проведения встречи.
        members (list[MemberResponseSchema]): Список участников встречи.
        transfer_counter (int): Счетчик переносов встречи.
        created_at (datetime): Время создания встречи.
        updated_at (datetime): Время последнего обновления встречи.
        description (Optional[str]): Описание встречи.
    """

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
