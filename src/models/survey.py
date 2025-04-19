from typing import List

from sqlalchemy import (
    Date, DateTime, Integer, ForeignKey,
    String, Text, JSON, UniqueConstraint, Enum)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.models import BaseTabitModel
from .enum import SurveysStatus


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

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    company_slug: Mapped[str] = mapped_column(
        ForeignKey("company.slug"), nullable=False)
    survey_slug: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.in_progress)
    cycles: Mapped[List["SurveyScheduleCycle"]] = relationship(
        back_populates="survey_schedule",
        cascade="all, delete-orphan")


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

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    date_start: Mapped[Date] = mapped_column(DateTime)
    survey_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("surveyschedule.id", ondelete="CASCADE"), nullable=False)
    survey_schedule: Mapped["SurveySchedule"] = relationship(
        back_populates="cycles")


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

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    # slug на случай если будут в дальнейшем еще тесты помимо эмоционального
    slug: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)


class SurveyData(BaseTabitModel):
    """
    Данные об прохождении теста.

    Назначение:
        Содержит данные об прохождении каждого теста.

    Поля:
        id: Идентификатор.
        survey_id: Номер расписания тестирований.
        survey_list_id: Идентификатор конкретного теста.
        user_id: Идентификатор пользователя прошедшего тест.
        answers: Ответы введенные пользователем.
        results: Результаты тестирования теста.

    """

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    survey_shedule_id: Mapped[int] = mapped_column(
        ForeignKey("surveyschedule.id", ondelete="CASCADE"), nullable=False)
    survey_list_id: Mapped[int] = mapped_column(
        ForeignKey("surveylist.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("companyuser.id", ondelete="CASCADE"), nullable=False)
    answers: Mapped[dict] = mapped_column(JSON)
    results: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (UniqueConstraint("survey_list_id", "user_id"),)
