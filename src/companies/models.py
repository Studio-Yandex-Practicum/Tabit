from datetime import date

from sqlalchemy import Boolean, Column, ForeignKey, Integer, List, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseTabitModel

from src.models import BaseLinkedTable, UserTabit

company_department = Table(
    'association_table',
    BaseTabitModel.metadata,
    Column('company_id', ForeignKey('company.id'), primary_key=True),
    Column('department_id', ForeignKey('department.id'), primary_key=True),
)


class Company(BaseTabitModel):
    """Модель компании."""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    company_name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    license_id: Mapped[int] = mapped_column(ForeignKey('license.id'))
    employees: Mapped['UserTabit'] = relationship(back_populates='company')
    # Следующие поля добавить в модель UserTabit
    # company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    # company: Mapped['Company'] = relationship(
    #     back_populates="employee", single_parent=True
    # )
    # __table_args__ = (UniqueConstraint('company_id'),)

    departments: Mapped[List['Department']] = relationship(
        secondary=company_department, back_populates='companies'
    )
    max_admins_count = Mapped[int]
    max_employees_count = Mapped[int]
    start_license_time: Mapped[date]
    end_license_time: Mapped[date]
    # В ERD этих полей нет! Есть в Figma.
    demo_mode: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    test_cycle_duration = Mapped[int]
    day_for_testing = Mapped[int]


class Department(BaseTabitModel):
    """Модель отдела."""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    department_name: Mapped[str] = mapped_column(unique=True)
    supervisor_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    employees: Mapped[List['UserTabit']] = relationship(
        back_populates='department'
    )


class Department_User(BaseLinkedTable):
    """Модель, связывающая пользователя с отделом."""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
