from datetime import date

from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import BaseTabitModel, str_uniq


class Company(BaseTabitModel):
    name: Mapped[str_uniq]
    description: Mapped[str]
    license_id: Mapped[int] = mapped_column(ForeignKey("license.id"))
    employees = relationship(
        'UserTabit', secondary='company_usertabit', back_populates='company'
    )
    employees: Mapped["UserTabit"] = relationship(
        "UserTabit", back_populates="usertabits"
    )
    departments: Mapped["Department"] = relationship(
        "Department", back_populates="companies"
    )
    max_admins_count = Mapped[int]
    max_employees_count = Mapped[int]
    start_license_time: Mapped[date]
    end_license_time: Mapped[date]

    demo_mode: Mapped[bool] = mapped_column(Boolean, nullable=False)
    test_cycle_duration = Mapped[int]
    day_for_testing = Mapped[int]


class Department(BaseTabitModel):
    pass


class UserTabit(BaseTabitModel):
    pass
