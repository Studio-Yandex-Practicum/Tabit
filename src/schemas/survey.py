from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SurveyScheduleCycleCreate(BaseModel):
    date_start: datetime


class SurveyScheduleCycleRead(SurveyScheduleCycleCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SurveyScheduleCreate(BaseModel):
    survey_tag: str
    status: str
    cycles: List[SurveyScheduleCycleCreate]


class SurveyScheduleRead(BaseModel):
    id: int
    survey_tag: str
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class SurveyAnswerCreate(BaseModel):
    survey_list_id: int
    answers: List[int]


class SurveyDataCreate(BaseModel):
    survey_shedule_id: int
    cycle_id: int
    answers: List[SurveyAnswerCreate]


class SurveyDataRead(BaseModel):
    id: int
    cycle_id: int
    results: Optional[dict]

    model_config = ConfigDict(from_attributes=True)
