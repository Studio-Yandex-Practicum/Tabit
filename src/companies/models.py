from datetime import date

from sqlalchemy import Boolean, Column, ForeignKey, List, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseTabitModel

from . import BaseUser, UserTags

company_department = Table(
    'association_table',
    BaseTabitModel.metadata,
    Column('company_id', ForeignKey('company.id'), primary_key=True),
    Column('department_id', ForeignKey('department.id'), primary_key=True),
)


class Company(BaseTabitModel):
    """Модель компании."""

    company_name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    license_id: Mapped[int] = mapped_column(ForeignKey('license.id'))
    # Поле employees(сотрудник) должно быть у модели Company?
    # Сотрудник связан с отделом, а уже отдел с Компанией.
    employees: Mapped['UserTabit'] = relationship(
        'UserTabit', back_populates='usertabits'
    )
    departments: Mapped[List['Department']] = relationship(
        secondary=company_department, back_populates='companies'
    )
    max_admins_count = Mapped[int]
    max_employees_count = Mapped[int]
    start_license_time: Mapped[date]
    end_license_time: Mapped[date]
    # В ERD этих полей нет! Есть в Figma.
    demo_mode: Mapped[bool] = mapped_column(Boolean, nullable=False)
    test_cycle_duration = Mapped[int]
    day_for_testing = Mapped[int]


class Department(BaseTabitModel):
    """Модель отдела."""

    department_name: Mapped[str] = mapped_column(unique=True)
    supervisor_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    employees: Mapped[List['UserTabit']] = relationship(
        back_populates='department'
    )


# Модель сотрудника делать должен не я. Набросал примерно.
# Нужно вставить только два последних поля.
class UserTabit(BaseUser):
    """Модель сотрудника."""

    role: Mapped[str]
    telegram_username: Mapped[str] = mapped_column(unique=True)
    # Нужна ли связь юзера с компанией? Или связь должна быть с отделом?
    company: Mapped[int] = mapped_column(ForeignKey('company.id'))
    start_date_employment: Mapped[date]
    end_date_employment: Mapped[date]
    birthday: Mapped[date]
    last_department: Mapped[int] = mapped_column(ForeignKey('department.id'))
    employee_position: Mapped[str]
    user_tags: Mapped['UserTags'] = relationship(
        'UserTags', back_populates='user_tags'
    )

    department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))
    department: Mapped["Department"] = relationship(
        back_populates='usertabits'
    )
