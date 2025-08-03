from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseTabitModel, CompanyUser, LuschersColorEnum, SurveysStatus
from src.models.annotations import int_pk


class SurveyCycleForCompany(BaseTabitModel):
    """
    Цикл опросов для компании.

    Назначение:
    - Содержит расписание опросов компании.

    Поля:
    - id: Идентификатор.
    - company_id: Идентификатор компании, для которой назначен цикл.
    - status: Статус цикла опросов.
    """

    id: Mapped[int_pk]
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='CASCADE'),
        nullable=False,
    )
    date: Mapped[date]
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.IN_PROGRESS
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'company_id={self.company_id!r}, '
            f'date={self.date!r}, '
            f'status={self.status!r})'
        )


class SurveyCycleForUser(BaseTabitModel):
    """
    Цикл опросов для конкретного пользователя.

    Назначение:
    - Содержит цикл опросов для конкретного пользователя.

    Поля:
    - id: Идентификатор.
    - survey_cycle_for_company_id: Идентификатор цикла опросов, к которому относится.
    - status: Статус опроса.
    - luscher_color_id: Идентификатор теста Люшера.
    """

    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'),
        nullable=False,
    )
    survey_cycle_for_company_id: Mapped[int] = mapped_column(
        ForeignKey('surveycycleforcompany.id', ondelete='CASCADE'),
        nullable=False,
    )
    date: Mapped[date]
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.IN_PROGRESS
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user_id={self.user_id!r}, '
            f'survey_cycle_for_company_id={self.survey_cycle_for_company_id!r}, '
            f'date={self.date!r}, '
            f'status={self.status!r})'
        )


class BaseLuscherColor(BaseTabitModel):
    """Базовая абстрактная модель для теста Люшера."""

    __abstract__ = True

    id: Mapped[int_pk]
    survey_cycle_for_user_id: Mapped[int] = mapped_column(
        ForeignKey('surveycycleforuser.id', ondelete='CASCADE'),
        nullable=False,
    )
    selection_1: Mapped[LuschersColorEnum]
    selection_2: Mapped[LuschersColorEnum]
    selection_3: Mapped[LuschersColorEnum]
    selection_4: Mapped[LuschersColorEnum]
    selection_5: Mapped[LuschersColorEnum]
    selection_6: Mapped[LuschersColorEnum]
    selection_7: Mapped[LuschersColorEnum]
    selection_8: Mapped[LuschersColorEnum]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'survey_cycle_for_user_id={self.survey_cycle_for_user_id!r}, '
            f'selection: {self.selection_1!r}, {self.selection_2!r}, '
            f'{self.selection_3!r}, {self.selection_4!r}, {self.selection_5!r}, '
            f'{self.selection_6!r}, {self.selection_7!r}, {self.selection_8!r})'
        )


class LuscherColorFirst(BaseLuscherColor):
    """
    Первый опрос по тесту Люшера.

    Назначение:
    - Сохраняет последовательность ответов пользователя.

    Поля:
    - id: Идентификатор.
    - survey_cycle_for_user_id: Идентификатор цикла опросов пользователя, к которому относится.
    - selection_<number>: Ответы пользователя, где number - номер ответа,
                          а значение - выбранный цвет.
    """


class LuscherColorSecond(BaseLuscherColor):
    """
    Второй опрос по тесту Люшера.

    Назначение:
    - Сохраняет последовательность ответов пользователя.

    Поля:
    - id: Идентификатор.
    - survey_cycle_for_user_id: Идентификатор цикла опросов пользователя, к которому относится.
    - selection_<number>: Ответы пользователя, где number - номер ответа,
                          а значение - выбранный цвет.
    """


class SociometryCycleForCompany(BaseTabitModel):
    """
    Цикл опроса по социометрии для всей компании.
    """

    id: Mapped[int_pk]
    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id', ondelete='CASCADE'), nullable=False
    )
    date: Mapped[date]
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.IN_PROGRESS
    )

    user_cycles: Mapped[List['SociometryCycleForUser']] = relationship(
        back_populates='company_cycle', cascade='all, delete-orphan'
    )


class SociometryCycleForUser(BaseTabitModel):
    """
    Индивидуальный цикл социометрии для пользователя.
    """

    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('companyuser.id', ondelete='CASCADE'), nullable=False
    )
    sociometry_cycle_for_company_id: Mapped[int] = mapped_column(
        ForeignKey('sociometrycycleforcompany.id', ondelete='CASCADE'), nullable=False
    )
    date: Mapped[date]
    status: Mapped[SurveysStatus] = mapped_column(
        Enum(SurveysStatus), default=SurveysStatus.IN_PROGRESS
    )

    company_cycle: Mapped['SociometryCycleForCompany'] = relationship(back_populates='user_cycles')
    test_results: Mapped[List['SociometryTestResult']] = relationship(
        back_populates='cycle', cascade='all, delete-orphan'
    )


class SociometryTestResult(BaseTabitModel):
    """
    Результат прохождения теста по социометрии.
    """

    id: Mapped[int_pk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey('companyuser.id'), nullable=False)
    sociometry_cycle_for_user_id: Mapped[int] = mapped_column(
        ForeignKey('sociometrycycleforuser.id'), nullable=False
    )

    user: Mapped['CompanyUser'] = relationship(back_populates='sociometry_results')
    cycle: Mapped['SociometryCycleForUser'] = relationship(back_populates='test_results')
    answers: Mapped[List['SociometryAnswer']] = relationship(
        back_populates='test_result', cascade='all, delete-orphan'
    )


class SociometryAnswer(BaseTabitModel):
    """
    Ответ на отдельный вопрос социометрии.
    """

    id: Mapped[int_pk]
    test_result_id: Mapped[int] = mapped_column(
        ForeignKey('sociometrytestresult.id'), nullable=False
    )
    question_key: Mapped[str]
    selected_user_id: Mapped[UUID] = mapped_column(ForeignKey('companyuser.id'), nullable=False)

    test_result: Mapped['SociometryTestResult'] = relationship(back_populates='answers')
    selected_user: Mapped['CompanyUser'] = relationship(back_populates='selected_in_answers')
