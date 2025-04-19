from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class SurveyScheduleCycleCreate(BaseModel):
    date: datetime


class SurveyScheduleCycleRead(SurveyScheduleCycleCreate):
    id: int
    survey_schedule_id: int

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


class SurveyAnswer(BaseModel):
    survey_list_id: int
    answers: List[int]


class SurveyDataCreate(BaseModel):
    survey_shedule_id: int
    cycle_id: int
    answers: List[SurveyAnswer]


class SurveyDataRead(BaseModel):
    survey_shedule_id: int
    cycle_id: int
    answers: List[int]

    model_config = ConfigDict(from_attributes=True)
