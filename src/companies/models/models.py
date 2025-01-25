"""
Модели для компании и департамента.
"""

from typing import List, Optional

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import LENGTH_NAME_COMPANY, LENGTH_NAME_DEPARTMENT
from src.models import (
    BaseTabitModel,
    description,
    int_pk,
    nullable_timestamp,
    url_link_field,
    int_zero,
)


class Company(BaseTabitModel):
    # TODO: Проверить тут докстринг и во всех моделях сделать подобный.
    # TODO: У всех моделей должен быть __repr__.
    # TODO: У всех моделей разобраться с полями datetime и их производных. Возможны ошибки.
    """
    Модель компании.

    Назначение:
        Хранит сведения о компании: название, описание, логотип, лицензии
        и ключевые ограничения (администраторы, сотрудники).

    Поля:
        id: Идентификатор компании.
        name: Название (уникальное).
        description: Описание (может быть пустым).
        logo: Логотип (может быть пустым).
        license_id: Ссылка на тип лицензии (может отсутствовать).
        max_admins_count: Максимальное кол-во администраторов.
        max_employees_count: Максимальное кол-во сотрудников.
        start_license_time: Дата начала действия лицензии (если есть).
        end_license_time: Дата окончания действия лицензии (если есть).
        departments: Список департаментов, связанных с компанией.
        employees: Список сотрудников, связанных с компанией.
    """

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(LENGTH_NAME_COMPANY), nullable=False)
    description: Mapped[description]
    logo: Mapped[url_link_field]
    departments: Mapped[List['Department']] = relationship(
        back_populates='company', cascade='all, delete'
    )
    employees: Mapped[List['UserTabit']] = relationship(  # noqa: F821
        back_populates='company', cascade='all, delete', lazy='selectin'
    )
    license_id: Mapped[Optional[int]] = mapped_column(ForeignKey('licensetype.id'), nullable=True)
    license: Mapped['LicenseType'] = relationship(back_populates='companies')  # noqa: F821
    max_admins_count: Mapped[int_zero]
    max_employees_count: Mapped[int_zero]
    start_license_time: Mapped[nullable_timestamp]
    end_license_time: Mapped[nullable_timestamp]
    is_active: Mapped[bool] = mapped_column(default=False)


class Department(BaseTabitModel):
    """
    Модель департамента.

    Назначение:
        Содержит информацию о департаменте внутри компании.

    Поля:
        id: Идентификатор департамента.
        name: Название департамента.
        company_id: Идентификатор компании, к которой относится департамент.
        supervisor_id: Идентификатор руководителя (если есть).
        company: Связь с моделью Company.
        employees: Список сотрудников, входящих в департамент.
    """

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(LENGTH_NAME_DEPARTMENT), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    company: Mapped['Company'] = relationship(back_populates='departments')
    supervisor_id: Mapped[Optional[int]] = mapped_column(ForeignKey('usertabit.id'), nullable=True)
    supervisor: Mapped['UserTabit'] = relationship(back_populates='supervisor')  # noqa: F821
    employees: Mapped[List['UserTabit']] = relationship(back_populates='current_department')  # noqa: F821
    employees_lost: Mapped[List['UserTabit']] = relationship(back_populates='last_department')  # noqa: F821
    __table_args__ = (UniqueConstraint('company_id', 'name', name='uq_company_department_name'),)
