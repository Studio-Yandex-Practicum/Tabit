"""
Модели для компании и департамента.
"""

from typing import List, Optional
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from src.models import BaseTabitModel
from src.users.models import UserTabit

from .types import (
    id_pk,
    company_name,
    department_name,
    license_id,
    company_id,
    user_id,
    description,
    logo,
    max_admins_count,
    max_employees_count,
    nullable_timestamp,
)


class Company(BaseTabitModel):
    """
    Модель компании.
    """

    id: Mapped[id_pk]
    name: Mapped[company_name]
    description: Mapped[description]
    logo: Mapped[logo]
    license_id: Mapped[license_id]
    max_admins_count: Mapped[max_admins_count]
    max_employees_count: Mapped[max_employees_count]
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
    """

    id: Mapped[id_pk]
    name: Mapped[department_name]
    company_id: Mapped[company_id]
    supervisor_id: Mapped[Optional[user_id]]  # TODO: Уточнить обязательность поля

    # Связь с компанией
    company: Mapped['Company'] = relationship('Company', back_populates='departments')

    # TODO: Уточнить поведение при удалении департамента: каскадное или запрет удаления?
    employees: Mapped[List['UserTabit']] = relationship(
        'UserTabit', back_populates='department'
    )

    # Ограничение на уникальность названия департамента в рамках компании
    __table_args__ = (
        UniqueConstraint('company_id', 'name', name='uq_company_department_name'),
    )
