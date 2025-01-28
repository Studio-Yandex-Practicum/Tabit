from pydantic import BaseModel
from typing import Optional, List
from datetime import date
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

    class Config:
        orm_mode = True


class StatusMeetingSchema(BaseModel):
    """
    Pydantic-схема для статусов мероприятий.
    """

    id: int
    name: str

    class Config:
        orm_mode = True


class ResultMeetingSchema(BaseModel):
    """
    Pydantic-схема для результатов мероприятий.
    """

    id: int
    name: str

    class Config:
        orm_mode = True


class TaskDBSchema(BaseModel):
    """Схема для задачи"""

    id: int
    name: str
    description: Optional[str] = None
    date_completion: date
    owner_id: int
    problem_id: int
    status: str
    file: Optional[int] = None


class TaskCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    date_completion: date
    owner_id: int
    status: str
    file: Optional[int] = None


class TaskUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date_completion: Optional[date] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    file: Optional[int] = None
