from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ResultSurveySchema(BaseModel):
    """
    Pydantic-схема для результатов опросов.
    """
    id: int
    name: str

    class Config:
        orm_mode = True


class MeetingBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для мероприятий.
    """
    name: str
    description: Optional[str]
    owner: int
    date: date
    status: int
    place: Optional[str]
    result: Optional[str]
    interest: bool = Field(default=False)
    found_solution: bool = Field(default=False)
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
    comments: List['CommentMeetingSchema'] = []

    class Config:
        orm_mode = True


class CommentMeetingBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для комментариев к мероприятиям.
    """
    comment: str
    interest: bool = Field(default=False)
    found_solution: bool = Field(default=False)
    owner: int
    meeting_id: int
    result: Optional[int]


class CommentMeetingCreateSchema(CommentMeetingBaseSchema):
    """
    Pydantic-схема для создания комментария.
    """
    pass


class CommentMeetingUpdateSchema(CommentMeetingBaseSchema):
    """
    Pydantic-схема для обновления комментария.
    """
    pass


class CommentMeetingSchema(CommentMeetingBaseSchema):
    """
    Pydantic-схема для отображения информации о комментарии.
    """
    id: int

    class Config:
        orm_mode = True


class SurveyBaseSchema(BaseModel):
    """
    Базовая Pydantic-схема для опросов.
    """
    name: str
    description: Optional[str]
    slug: str
    status: int
    result: Optional[int]
    created_at: datetime


class SurveyCreateSchema(SurveyBaseSchema):
    """
    Pydantic-схема для создания опроса.
    """
    pass


class SurveyUpdateSchema(SurveyBaseSchema):
    """
    Pydantic-схема для обновления информации об опросе.
    """
    pass


class SurveySchema(SurveyBaseSchema):
    """
    Pydantic-схема для отображения информации об опросе.
    """
    id: int

    class Config:
        orm_mode = True


class SurveyUserSchema(BaseModel):
    """
    Pydantic-схема для связи пользователей с опросами.
    """
    id: int
    survey_id: int
    user_id: int

    class Config:
        orm_mode = True


class DateSurveySchema(BaseModel):
    """
    Pydantic-схема для дат, связанных с опросами.
    """
    id: int
    date: date
    survey_id: int

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


class StatusSurveySchema(BaseModel):
    """
    Pydantic-схема для статусов опросов.
    """
    id: int
    name: str

    class Config:
        orm_mode = True
