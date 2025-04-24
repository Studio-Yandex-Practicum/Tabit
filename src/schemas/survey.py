from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SurveyScheduleCycleCreate(BaseModel):
    """
    Схема создания циклов в расписании тестирований.

    Назначение:
        Определяет структуру данных для создания циклов в расписании.
    Параметры:
        cycle_number: номер цикла в расписании (6 циклов максимум).
        date_start: дата начала тестирования.
    """

    cycle_number: int = Field(..., ge=1, le=6)
    date_start: datetime

    @field_validator('date_start')
    @classmethod
    def check_datetime(cls, value: datetime) -> datetime:
        if value <= datetime.now():
            raise ValueError(
                'Дата начала тестирования  '
                'не может быть меньше текущего времени'
            )
        return value


class SurveyScheduleCycleRead(BaseModel):
    """
    Схема получения циклов в расписании.

    Назначение:
        Определяет структуру ответа получения циклов внутри расписания.
    Параметры:
        cycle_number: номер цикла в расписании (6 циклов максимум).
        date_start: дата начала тестирования.
    """
    cycle_number: int 
    date_start: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyScheduleCreate(BaseModel):
    """
    Схема создания расписания.

    Назначение:
        Определяет структуру запроса для создания расписания.
    Параметры:
        survey_tag: Таг определяетщий вид тестирования.
        status: текущий статус расписания.
        cycles: список циклов тестирований.
    """

    survey_tag: str
    status: str
    cycles: List[SurveyScheduleCycleCreate]

    class Config:
        json_schema_extra = {
            'example': {
                'survey_tag': 'EMO',
                'status': 'IN_PROGRESS',
                'cycles': [
                    {'cycle_number': 1, 'date_start': '2025-04-22'},
                    {'cycle_number': 2, 'date_start': '2025-05-22'},
                ],
            }
        }


class SurveyScheduleUpdate(BaseModel):
    """
    Схема обновления расписания.

    Назначение:
        Определяет структуру запроса для создания расписания.
    Параметры:
        survey_tag: Таг определяетщий вид тестирования. (Опционально)
        status: текущий статус расписания. (Опционально)
        cycles: список циклов тестирований. (Опционально)
    """

    survey_tag: str | None = None
    status: str | None = None
    cycles: List[SurveyScheduleCycleCreate] | None = None


class SurveyScheduleRead(BaseModel):
    """
    Схема получения расписания.

    Назначение:
        Определяет структуру данных для ответа с информацией об расписании.
    Параметры:
        id: Идентификатор
        survey_tag: Таг определяетщий вид тестирования.
        created_at: Дата создания расписания.
        status: текущий статус расписания.
    """

    id: int
    survey_tag: str
    created_at: datetime
    status: str
    cycles: List[SurveyScheduleCycleRead]

    model_config = ConfigDict(from_attributes=True)


class SurveyAnswerCreate(BaseModel):
    """
    Схема создания ответов.

    Назначение:
        Определяет структуру запроса на создание ответов тестов.
    Параметры:
        survey_list_id: Уникальный идентификатор теста.
        answers: Список ответов.
    """

    survey_list_id: int
    answers: List[int]


class SurveyDataCreate(BaseModel):
    """
    Схема создания данных об прохождении тестов.

    Назначение:
        Определяет структуру запроса на создание данных об прохождении теста сотрудника.
    Параметры:
        survey_shedule_id: Идентификатор расписания к которому привязаны данные.
        cycle_id: Идентификатор цикла к которому привязаны данные.
        answers: Список ответов.
    """

    survey_shedule_id: int
    cycle_id: int
    answers: List[SurveyAnswerCreate]

    class Config:
        json_schema_extra = {
            'example': {
                'survey_shedule_id': 1,
                'cycle_id': 2,
                'answers': [
                    {'survey_list_id': 1, 'answers': [1, 2, 3, 4, 5, 6]},
                    {'survey_list_id': 2, 'answers': [1, 2, 3, 4]},
                ],
            }
        }


class SurveyDataRead(BaseModel):
    """
    Схема получения данных об прохождении тестов.

    Назначение:
        Определяет структуру данных для ответа на запрос данных о прохождении теста.
    Параметры:
        id: Идентификатор записи.
        cycle_id: Идентификатор цикла к которому привязаны данные.
        results: Окончательный результат тестирования на основе всех тестов.
    """

    id: int
    cycle_id: int
    results: dict | None = None

    model_config = ConfigDict(from_attributes=True)
