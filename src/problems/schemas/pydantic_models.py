from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# TODO Прописать схемы
class ResultMeetingSchema(BaseModel):
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


# class MeetingSchema(MeetingBaseSchema):
#     id: int
#     comments: List['CommentMeetingSchema'] = []
#     messages: List['MessageMeetingSchema'] = []

#     class Config:
#         orm_mode = True
