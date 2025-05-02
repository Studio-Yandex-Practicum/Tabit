from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy import JSON, Date, Enum, ForeignKey, Integer
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

    cycles_dates: Mapped[List[date]] = mapped_column(JSON, nullable=False)
    attempts: Mapped[List["SurveyData"]] = relationship(
        "SurveyData", back_populates="schedule", cascade="all, delete-orphan")


class SurveyData(BaseTabitModel):
    """
    Данные об прохождении теста.

    Назначение:
        Содержит данные об прохождении теста.

    Поля:
        id: Идентификатор.
        survey_shedule_id: Номер расписания тестирований.
        user_id: Идентификатор пользователя прошедшего тест.
        cycle_id: Идентификатор цикла к которому относится выполненный тест.
        answers: Ответы введенные пользователем.
        results: Окончательный результат тестирования.

    Связи (атрибут - Модель):
        schedule - > SurveySchedule
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shedule_id: Mapped[int] = mapped_column(
        ForeignKey('surveyschedule.id', ondelete='CASCADE'), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'), nullable=False
    )
    company_slug: Mapped[str] = mapped_column(
        ForeignKey('company.slug', ondelete='CASCADE'), nullable=False
    )
    cycle_date: Mapped[date] = mapped_column(Date, nullable=False)

    answers: Mapped[dict] = mapped_column(JSON, nullable=False)
    results: Mapped[dict | None] = mapped_column(JSON)
    schedule: Mapped[SurveySchedule] = relationship("SurveySchedule", back_populates="attempts")
