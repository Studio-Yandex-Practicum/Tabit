from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SurveyScheduleCycleCreate(BaseModel):
    cycle_number: int
    date_start: datetime


class SurveyScheduleCycleRead(SurveyScheduleCycleCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SurveyScheduleCreate(BaseModel):
    survey_tag: str
    status: str
    cycles: List[SurveyScheduleCycleCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "survey_tag": "EMO",
                "status": "IN_PROGRESS",
                "cycles": [
                    {
                        "cycle_number": 1,
                        "date_start": "2025-04-22"
                    },
                    {
                        "cycle_number": 2,
                        "date_start": "2025-05-22"
                    }
                ]
            }
        }


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

    class Config:
        json_schema_extra = {
            "example": {
                "survey_shedule_id": 1,
                "cycle_id": 2,
                "answers": [
                    {
                        "survey_list_id": 1,
                        "answers": [
                            1, 2, 3, 4, 5, 6
                        ]
                    },
                    {
                        "survey_list_id": 2,
                        "answers": [
                            1, 2, 3, 4
                        ]
                    }
                ]
            }
        }


class SurveyDataRead(BaseModel):
    id: int
    cycle_id: int
    results: Optional[dict]

    model_config = ConfigDict(from_attributes=True)
