"""
Модели для компании и департамента.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from src.models import BaseTabitModel

if TYPE_CHECKING:
    from src.users.models import UserTabit

from .types import id_pk, nullable_timestamp

from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import mapped_column

from ..constants import (
    COMPANY_NAME_LENGTH,
    DEPARTMENT_NAME_LENGTH,
    MAX_ADMINS_COUNT_DEFAULT,
    MAX_EMPLOYEES_COUNT_DEFAULT,
)


class Company(BaseTabitModel):
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

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column(String(COMPANY_NAME_LENGTH), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # TODO: обсудить опциональность лицензий
    license_id: Mapped[Optional[int]] = mapped_column(ForeignKey('licensetype.id'), nullable=True)
    max_admins_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=MAX_ADMINS_COUNT_DEFAULT
    )
    max_employees_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=MAX_EMPLOYEES_COUNT_DEFAULT
    )
    start_license_time: Mapped[nullable_timestamp]
    end_license_time: Mapped[nullable_timestamp]

    # TODO: Обсудить каскадное удаление департаментов при удалении компании или отправляем в архив
    departments: Mapped[List['Department']] = relationship(
        'Department', back_populates='company', cascade='all'
    )

    # TODO: Уточнить необходимость каскадного удаления сотрудников при удалении компании или в архив
    employees: Mapped[List['UserTabit']] = relationship(
        'UserTabit', back_populates='company', cascade='all', lazy='selectin'
    )


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

    id: Mapped[id_pk]
    name: Mapped[str] = mapped_column(String(DEPARTMENT_NAME_LENGTH), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    # TODO: Уточнить опциональность поля
    supervisor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('usertabit.uuid'), nullable=True
    )

    # Связь с компанией
    company: Mapped['Company'] = relationship('Company', back_populates='departments')

    # TODO: Уточнить поведение при удалении департамента: каскадное или запрет удаления?
    employees: Mapped[List['UserTabit']] = relationship('UserTabit', back_populates='department')

    # Ограничение на уникальность названия департамента в рамках компании
    __table_args__ = (UniqueConstraint('company_id', 'name', name='uq_company_department_name'),)
