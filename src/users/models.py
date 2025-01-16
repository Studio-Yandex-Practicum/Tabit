from datetime import date
from typing import Optional, List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import BaseTabitModel
from src.companies.models import Department, Company

# Нужно место, где это будет хранится.
LENGTH_NAME_USER: int = 746
LENGTH_SMALL_NAME: int = 30
LENGTH_TELEGRAM_USERNAME = 100


class BaseUser(SQLAlchemyBaseUserTableUUID, BaseTabitModel):
    """Базовая модель пользователей. Абстрактная модель"""

    name: Mapped[str] = mapped_column(String(LENGTH_NAME_USER))
    surname: Mapped[str] = mapped_column(String(LENGTH_NAME_USER))
    patronymic: Mapped[str] = mapped_column(String(LENGTH_NAME_USER))
    phone_number: Mapped[str]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id},'
            f'name={self.name},'
            f'surname={self.surname},'
            f'patronymic={self.patronymic})'
        )


class BaseTag(BaseTabitModel):
    """Базовая модель тэгов. Абстрактная модель"""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(LENGTH_SMALL_NAME))

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'


class AssociationUserTags(BaseTabitModel):
    """Связная таблица UserTabit и Tag."""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    left_id: Mapped[int] = mapped_column(
        ForeignKey('left_table.id'), primary_key=True
    )
    right_id: Mapped[int] = mapped_column(
        ForeignKey('right_table.id'), primary_key=True
    )
    user: Mapped['UserTabit'] = relationship(back_populates='tags')
    tag: Mapped['Tag'] = relationship(back_populates='user')


class Role(BaseTag):
    """Модель ролей пользователей."""

    user: Mapped[List['UserTabit']] = relationship(back_populates='role')


class Tag(BaseTag):
    """Модель тэгов пользователей."""

    user: Mapped[List['AssociationUserTags']] = relationship(
        back_populates='tag'
    )


class UserTabit(BaseUser):
    """Модель пользователей ресурс Tabit."""

    role_id: Mapped[int] = mapped_column(ForeignKey('role.id'))
    role: Mapped['Role'] = relationship(back_populates='user')

    tags: Mapped[List['AssociationUserTags']] = relationship(
        back_populates='user'
    )

    telegram_username: Mapped[str] = mapped_column(
        String(LENGTH_TELEGRAM_USERNAME), unique=True
    )
    start_date_employment: Mapped[date]
    end_date_employment: Mapped[date]
    birthday: Mapped[date]

    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    company: Mapped['Company'] = relationship(back_populated='user')
    current_department_id: Mapped[int] = mapped_column(
        ForeignKey('department.id')
    )
    current_department: Mapped['Department'] = relationship(
        back_populates='department.id'
    )
    last_department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('department.id')
    )
    last_department: Mapped['Department'] = relationship(
        back_populates='department.id'
    )

    department_transition_date: Mapped[date]
    employee_position: Mapped[str]


class TabitAdminUser(BaseUser):
    """Модель пользователей-админов сервиса Tabit."""

    pass
