from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .enums import MeetingStatus


class MeetingBaseSchema(BaseModel):
    """
    Параметры:
        title: Заголовок встречи.
        description: Описание.
        owner: Автор встречи.
        date: Дата встречи.
        status: Статус встречи.
        place: Место встречи.
        result: Результаты встречи.
        file: К встречи могут быть прикреплены файлы.
    """

    title: str
    description: Optional[str]
    owner: Optional[int]
    date: date
    status: MeetingStatus
    place: Optional[str]
    result: Optional[int]
    file: Optional[int]

    model_config = ConfigDict(
        title = "Схема мероприятий",
        description = "Базовая схема для мероприятий"
    )


class MeetingCreateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для создания мероприятия.
    """

    model_config = ConfigDict(
        title = "Схема создания мероприятий",
        description = "Схема для создания мероприятий"
    )


class MeetingUpdateSchema(MeetingBaseSchema):
    """
    Pydantic-схема для обновления информации о мероприятии.
    """

    model_config = ConfigDict(
        title = "Схема изменения мероприятий",
        description = "Схема для обновления информации о мероприятии"
    )


class MeetingSchema(MeetingBaseSchema):
    """
    Параметры:
        id: идентефикатор.
        members: участники встречи.
    """

    id: int
    members: List[int] = []

    model_config = ConfigDict(
        from_attributes=True,
        title = "Схема мероприятия",
        description = "Схема для отображения информации о мероприятии"
    )


class StatusMeetingSchema(BaseModel):
    """
    Параметры:
        id: идентефикатор.
        name: название мероприятия.
    """

    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        title = "Схема статусов",
        description = "Схема для статусов мероприятий"
    )


class ResultMeetingSchema(BaseModel):
    """
    Параметры:
        id: идентефикатор.
        name: название мероприятия.
    """

    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        title = "Схема результатов",
        description = "Схема для результатов мероприятий"
    )
