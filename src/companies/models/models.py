"""
Модели для компании и департамента.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import LENGTH_NAME_COMPANY, LENGTH_NAME_DEPARTMENT
from src.database.annotations import (
    description,
    int_pk,
    int_zero,
    slug,
    timestamp_nullable,
    url_link_field,
)
from src.database.models import BaseTabitModel

if TYPE_CHECKING:
    from src.problems.models.problem_models import Problem
    from src.tabit_management.models import LicenseType
    from src.users.models import TagUser, UserTabit


class Company(BaseTabitModel):
    """
    Модель компании.

    Назначение:
        Хранит сведения о компании: название, описание, логотип, лицензии
        и ключевые ограничения (администраторы, сотрудники).

    Поля:
        id: Идентификатор компании.
        name: Название.
        description: Описание (может быть пустым).
        logo: Логотип (может быть пустым).
        license_id: Ссылка на тип лицензии (может отсутствовать).
        max_admins_count: Максимальное кол-во администраторов.
        max_employees_count: Максимальное кол-во сотрудников.
        start_license_time: Дата начала действия лицензии (если есть).
        end_license_time: Дата окончания действия лицензии (если есть).
        is_active: bool - активна ли лицензия.
        slug: Короткая строка для пути к эндпоинту.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        departments - Department;
        employees - UserTabit;
        license - LicenseType;
        tags_users - TagUser: админ от компании может придумывать свои тэги для пользователей.
        problems - Problem: связь к созданным проблемам, определенной компании;
    """

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(LENGTH_NAME_COMPANY), nullable=False)
    description: Mapped[description]
    logo: Mapped[url_link_field]
    departments: Mapped[List['Department']] = relationship(
        back_populates='company', cascade='all, delete'
    )
    employees: Mapped[List['UserTabit']] = relationship(
        back_populates='company', cascade='all, delete', lazy='selectin'
    )
    problems: Mapped[List['Problem']] = relationship(
        back_populates='company', cascade='all, delete-orphan'
    )
    license_id: Mapped[Optional[int]] = mapped_column(ForeignKey('licensetype.id'), nullable=True)
    license: Mapped[Optional['LicenseType']] = relationship(back_populates='companies')
    max_admins_count: Mapped[int_zero]
    max_employees_count: Mapped[int_zero]
    start_license_time: Mapped[timestamp_nullable]
    end_license_time: Mapped[timestamp_nullable]
    is_active: Mapped[bool] = mapped_column(default=False)
    tags_users: Mapped[List['TagUser']] = relationship(
        back_populates='company', cascade='all, delete-orphan'
    )
    slug: Mapped[slug]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'is_active={self.is_active!r})'
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
        slug: Короткая строка для пути к эндпоинту.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        company - Company.
    """

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(LENGTH_NAME_DEPARTMENT), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    company: Mapped['Company'] = relationship(back_populates='departments')
    # employees: Mapped[List['UserTabit']] = relationship(back_populates='current_department')
    # employees_lost: Mapped[List['UserTabit']] = relationship(back_populates='last_department')
    slug: Mapped[slug]

    __table_args__ = (UniqueConstraint('company_id', 'name', name='uq_company_department_name'),)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'company_id={self.company_id!r})'
        )
