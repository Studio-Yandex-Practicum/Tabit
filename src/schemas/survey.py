from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.models.enum import SurveysStatus, SurveysTags


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
    # TODO : валидаторы даты
    survey_tag: SurveysTags = Field(..., description='таг вида тестирования')
    status: SurveysStatus = Field(..., description='статус расписания')
    cycles_dates: List[date] = Field(..., min_length=1, max_length=6)

    class Config:
        json_schema_extra = {
            'example': {
                'survey_tag': 'Определение эмоционального состояния',
                'status': 'В работе',
                'cycles_dates': [
                    date.today(), date.today()
                ]
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
    # TODO : добавить валидатор даты
    survey_tag: SurveysTags | None = Field(None, description='таг вида тестирования')
    status: SurveysStatus | None = Field(None, description='статус расписания')
    cycles_dates: List[date] | None = Field(
        None, description='список циклов в расписании (6 циклов максимум)'
    )


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
    cycles_dates: List[date]

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

    test_number: int
    answers: List[int]
    results: str | None = None

    class Config:
        model_config = {'frozen': False}


class SurveyDataCreate(BaseModel):
    """
    Схема создания данных об прохождении тестов.

    Назначение:
        Определяет структуру запроса на создание данных об прохождении теста сотрудника.
    Параметры:
        survey_shedule_id: Идентификатор расписания к которому привязаны данные.
        cycle_date: Дата цикла в расписании для сопостравления.
        answers: Список ответов.
    """

    shedule_id: int = Field(..., description='Идентификатор расписания')
    cycle_date: date = Field(..., description='Дата цикла')
    answers: List[SurveyAnswerCreate] = Field(..., description='Список ответов')
    results: dict | None = None

    class Config:
        json_schema_extra = {
            'example': {
                'shedule_id': 1,
                'cycle_date': "2027-05-10",
                'answers': [
                    {'test_number': 1, 'answers': [1, 2, 3, 4, 5, 6], "result": None},
                    {'test_number': 2, 'answers': [1, 2, 3, 4], "result": None},
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
        shedule_id: Идентификатор расписания к которому привязаны данные.
        cycle_id: Идентификатор цикла к которому привязаны данные.
        results: Окончательный результат тестирования на основе всех тестов.
    """

    id: int
    shedule_id: int
    cycle_date: date
    results: dict | None = None

    model_config = ConfigDict(from_attributes=True)
