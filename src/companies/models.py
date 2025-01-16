from datetime import date

from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import BaseTabitModel
from . import BaseUser, UserTags


class Company(BaseTabitModel):
    """Модель компании."""
    company_name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]
    license_id: Mapped[int] = mapped_column(ForeignKey('license.id'))
    employees: Mapped['UserTabit'] = relationship(
        'UserTabit', back_populates='user_tabits'
    )
    departments: Mapped["Department"] = relationship(
        "Department", back_populates='companies'
    )
    max_admins_count = Mapped[int]
    max_employees_count = Mapped[int]
    start_license_time: Mapped[date]
    end_license_time: Mapped[date]

    demo_mode: Mapped[bool] = mapped_column(Boolean, nullable=False)
    test_cycle_duration = Mapped[int]
    day_for_testing = Mapped[int]


class Department(BaseTabitModel):
    """Модель отдела."""
    department_name: Mapped[str] = mapped_column(unique=True)
    supervisor_id: Mapped[int] = mapped_column(ForeignKey('user_tabit.uuid'))


class UserTabit(BaseUser):
    """Модель сотрудника."""
    role: Mapped[str]
    telegram_username: Mapped[str] = mapped_column(unique=True)
    company: Mapped[int] = mapped_column(ForeignKey('company.id'))
    start_date_employment: Mapped[date]
    end_date_employment: Mapped[date]
    birthday: Mapped[date]
    last_department: Mapped[int] = mapped_column(ForeignKey('department.id'))
    employee_position: Mapped[str]
    user_tags: Mapped['UserTags'] = relationship(
        'UserTags', back_populates='user_tags'
    )
