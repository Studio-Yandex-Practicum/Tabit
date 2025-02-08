from datetime import date
from typing import List, Optional

<<<<<<< HEAD
from pydantic import BaseModel
=======
from pydantic import BaseModel, ConfigDict
>>>>>>> 6dce2ec (закончил с роутами лицензии, добавил тесты итд)

from .enums import MeetingStatus


class MeetingBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для мероприятий.
    """

    title: str
    description: Optional[str]
    owner: Optional[int]
    date: date
    status: MeetingStatus
    place: Optional[str]
    result: Optional[int]
    file: Optional[int]


class MeetingCreateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для создания мероприятия.
    """

    pass


class MeetingUpdateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для обновления информации о мероприятии.
    """

    pass


class MeetingSchema(MeetingBaseSchema):
    """
    Pydantic-схема для отображения информации о мероприятии.
    """

    id: int
    members: List[int] = []

    model_config = ConfigDict(from_attributes=True)


class StatusMeetingSchema(BaseModel):
    """
    Pydantic-схема для статусов мероприятий.
    """

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ResultMeetingSchema(BaseModel):
    """
    Pydantic-схема для результатов мероприятий.
    """

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
