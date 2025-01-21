from datetime import date

from sqlalchemy import ForeignKey, Integer, List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import BaseTabitModel

from src.models import BaseLinkedTable, LicenseType, UserTabit


class CompanyDepartment(BaseTabitModel):
    """Модель, связывающая компанию с отделом."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))


class Company(BaseTabitModel):
    """Модель компании."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    license: Mapped['LicenseType'] = relationship(back_populates='company')
    # TODO Следующие поля добавить в модель LicenseType
    # company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    # company: Mapped['Company'] = relationship(back_populates='licensetype')
    employees: Mapped['UserTabit'] = relationship(back_populates='company')
    # TODO Следующие поля добавить в модель UserTabit
    # company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    # company: Mapped['Company'] = relationship(
    #     back_populates="employee", single_parent=True
    # )
    # __table_args__ = (UniqueConstraint('company_id'),)

    departments: Mapped[List['Department']] = relationship(
        secondary=CompanyDepartment, back_populates='companies'
    )
    max_admins_count = Mapped[int]
    max_employees_count = Mapped[int]
    start_license_time: Mapped[date]
    end_license_time: Mapped[date]


class Department(BaseTabitModel):
    """Модель отдела."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_name: Mapped[str] = mapped_column(unique=True)
    supervisor_id: Mapped[int] = mapped_column(ForeignKey('usertabit.uuid'))
    employees: Mapped[List['UserTabit']] = relationship(back_populates='department')


class Department_User(BaseLinkedTable):
    """Модель, связывающая пользователя с отделом."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
