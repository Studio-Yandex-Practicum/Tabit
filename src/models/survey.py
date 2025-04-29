from typing import List
from uuid import UUID

from sqlalchemy import JSON, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseTabitModel

from .enum import SurveysStatus, SurveysTags


class SurveySchedule(BaseTabitModel):
    """
    Модель расписания тестирований.

    Назначение:
        Содержит расписание тестирований компании.

    Поля:
        id: Идентификатор.
        company_id: Идентифифкатор компании создавшей расписание.
        survey_slug: slug для выборки нужных тестов.
        status: Статус расписания тестирований.

    Связи (атрибут - Модель):
        cycles: Cycle: циклы тестирований внутри одного расписания.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_slug: Mapped[str] = mapped_column(
        ForeignKey('company.slug', ondelete='CASCADE'), nullable=False
    )
    survey_tag: Mapped[SurveysTags] = mapped_column(Enum(SurveysTags))
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.IN_PROGRESS
    )

    cycles: Mapped[List['SurveyScheduleCycle']] = relationship(
        back_populates='survey_schedule', cascade='all, delete-orphan', lazy='joined'
    )


class SurveyScheduleCycle(BaseTabitModel):
    """
    Модель для циклов тестирования

    Назначение:
        Содержит даты начала циклов тестирования.

    Поля:
        id: Идентификатор.
        date_start: Дата начала тестирования.
        survey_shedule_id: Идентификатор расписания тестирования.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cycle_number: Mapped[int] = mapped_column(Integer)
    date_start: Mapped[Date] = mapped_column(Date)
    survey_schedule_id: Mapped[int] = mapped_column(
        ForeignKey('surveyschedule.id', ondelete='CASCADE'), nullable=False
    )

    survey_schedule: Mapped['SurveySchedule'] = relationship(back_populates='cycles')


class SurveyList(BaseTabitModel):
    """
    Модель для списка тестов.

    Назначение:
        Содержит спиок тестов.

    Поля:
        id: Идентификатор.
        title: Название теста.
        slug: Идентификатор с помощью которого можно объединить несколько
              тестов в одно тестирование.
        description: Описание теста.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    tag: Mapped[SurveysTags] = mapped_column(Enum(SurveysTags))
    description: Mapped[str | None] = mapped_column(Text)


class SurveyData(BaseTabitModel):
    """
    Данные об прохождении теста.

    Назначение:
        Содержит данные об прохождении каждого теста.

    Поля:
        id: Идентификатор.
        survey_shedule_id: Номер расписания тестирований.
        user_id: Идентификатор пользователя прошедшего тест.
        cycle_id: Идентификатор цикла к которому относится выполненный тест.
        answers: Ответы введенные пользователем.
        results: Окончательный результат тестирования.

    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    survey_shedule_id: Mapped[int] = mapped_column(
        ForeignKey('surveyschedule.id', ondelete='CASCADE'), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'), nullable=False
    )
    company_slug: Mapped[str] = mapped_column(
        ForeignKey('company.slug', ondelete='CASCADE'), nullable=False
    )
    cycle_id: Mapped[int] = mapped_column(
        ForeignKey('surveyschedulecycle.id', ondelete='CASCADE'), nullable=False
    )
    results: Mapped[dict | None] = mapped_column(JSON)

    answers: Mapped[List['SurveyAnswer']] = relationship(
        back_populates='survey_data', cascade='all, delete-orphan'
    )


class SurveyAnswer(BaseTabitModel):
    """
    Модель для ответов - результатов тестирования пользователя.

    Назначение:
        Содержит информацию о каждом этапе таста с его ответами и результатами.

    Поля:
        id: Идентификатор.
        survey_data_id: Идентификатор таблицы "Данные об прохождении теста".
        survey_list_id: Идентификатор конкретного теста.
        answer: Ответы введенные пользователем.
        results: Результаты теста.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    survey_data_id: Mapped[int] = mapped_column(ForeignKey('surveydata.id'))
    survey_list_id: Mapped[int] = mapped_column(
        ForeignKey('surveylist.id', ondelete='CASCADE'), nullable=False
    )
    answer: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON)

    survey_data: Mapped['SurveyData'] = relationship(back_populates='answers')
