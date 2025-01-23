from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.companies.models.models import Company, Department
from src.constants import LENGTH_TELEGRAM_USERNAME
from src.models import BaseTabitModel, BaseTag, BaseUser, int_pk


class AssociationUserTags(BaseTabitModel):
    """Связная таблица UserTabit и Tag."""

    id: Mapped[int_pk]
    left_id: Mapped[UUID] = mapped_column(
        ForeignKey('usertabit.uuid'), primary_key=True
    )
    right_id: Mapped[int] = mapped_column(ForeignKey('tag.id'), primary_key=True)
    user: Mapped['UserTabit'] = relationship(back_populates='tags')
    tag: Mapped['Tag'] = relationship(back_populates='user')


class Role(BaseTag):
    """Модель ролей пользователей."""

    user: Mapped[List['UserTabit']] = relationship(back_populates='role')


class Tag(BaseTag):
    """Модель тэгов пользователей."""

    user: Mapped[List['AssociationUserTags']] = relationship(back_populates='tag')


class UserTabit(BaseUser):
    """Модель пользователей ресурс Tabit."""

    role_id: Mapped[int] = mapped_column(ForeignKey('role.id'))
    role: Mapped['Role'] = relationship(back_populates='user')

    tags: Mapped[List['AssociationUserTags']] = relationship(back_populates='user')

    telegram_username: Mapped[str] = mapped_column(
        String(LENGTH_TELEGRAM_USERNAME), unique=True
    )
    birthday: Mapped[date]
    start_date_employment: Mapped[date]
    end_date_employment: Mapped[date]

    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populated='user')
    current_department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))
    current_department: Mapped['Department'] = relationship(
        back_populates='department.id'
    )
    last_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('department.id')
    )
    last_department: Mapped['Department'] = relationship(back_populates='department.id')

    department_transition_date: Mapped[date]
    employee_position: Mapped[str]
