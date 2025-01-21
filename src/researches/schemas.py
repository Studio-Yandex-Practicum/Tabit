from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class StatusMeetingSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ResultMeetingSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class StatusSurveySchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ResultSurveySchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class MeetingBaseSchema(BaseModel):
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
    pass


class MeetingUpdateSchema(MeetingBaseSchema):
    pass


class MeetingSchema(MeetingBaseSchema):
    id: int
    comments: List['CommentMeetingSchema'] = []
    messages: List['MessageMeetingSchema'] = []

    class Config:
        orm_mode = True


class CommentMeetingBaseSchema(BaseModel):
    owner: int
    result: Optional[int]
    meeting_id: int
    interest: bool = Field(default=False)
    found_solution: bool = Field(default=False)
    comment: str


class CommentMeetingCreateSchema(CommentMeetingBaseSchema):
    pass


class CommentMeetingSchema(CommentMeetingBaseSchema):
    id: int

    class Config:
        orm_mode = True


class SurveyBaseSchema(BaseModel):
    name: str
    description: Optional[str]
    slug: str
    status: int
    result: Optional[int]
    created_at: datetime


class SurveyCreateSchema(SurveyBaseSchema):
    pass


class SurveySchema(SurveyBaseSchema):
    id: int

    class Config:
        orm_mode = True


class SurveyUserBaseSchema(BaseModel):
    survey_id: int
    user_id: int


class SurveyUserCreateSchema(SurveyUserBaseSchema):
    pass


class SurveyUserSchema(SurveyUserBaseSchema):
    id: int

    class Config:
        orm_mode = True


class DateSurveyBaseSchema(BaseModel):
    date: date
    survey_id: int


class DateSurveyCreateSchema(DateSurveyBaseSchema):
    pass


class DateSurveySchema(DateSurveyBaseSchema):
    id: int

    class Config:
        orm_mode = True


class MessageMeetingBaseSchema(BaseModel):
    owner: int
    meeting_id: int
    text: str
    created_at: datetime


class MessageMeetingCreateSchema(MessageMeetingBaseSchema):
    pass


class MessageMeetingSchema(MessageMeetingBaseSchema):
    id: int

    class Config:
        orm_mode = True
