from typing import List

from sqlalchemy import Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseTabitModel, BaseUser, int_pk, name_field


class TabitAdminUser(BaseUser):
    """Модель пользователей-админов сервиса Tabit."""

    pass


class LicenseType(BaseTabitModel):
    """Модель типов лицензий."""

    id: Mapped[int_pk]
    name: Mapped[name_field]
    # TODO: Убрать единицу из day_precision=1 в константы.
    license_term: Mapped[Interval] = mapped_column(Interval(day_precision=1))
    max_admins_count: Mapped[int]
    max_employees_count: Mapped[int]

    companies: Mapped[List['Company']] = relationship(back_populates='license')
