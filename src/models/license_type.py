from typing import List

from sqlalchemy import Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.annotations import int_pk, license_name_field
from src.models import BaseTabitModel
from src.core.constants.tabit_management import DEFAULT_NUMBER_DEY_LICENSE
from src.models.types import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.types import Company

class LicenseType(BaseTabitModel):
    """
    Модель типов лицензий.

    Назначение:
        Хранит сведения о лицензии, выдаваемые сервисом компаниям.

    Поля:
        id: Идентификатор компании.
        name: Название.
        license_term: Срок действия лицензии в днях.
        max_admins_count: Максимально допустимое количество админов у компании.
        max_employees_count: Максимально допустимое количество сотрудников у компании.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        companies - Company: чтоб определить, каким компаниям выдана.
    """

    id: Mapped[int_pk]
    name: Mapped[license_name_field]
    license_term: Mapped[Interval] = mapped_column(
        Interval(day_precision=DEFAULT_NUMBER_DEY_LICENSE)
    )
    max_admins_count: Mapped[int]
    max_employees_count: Mapped[int]

    companies: Mapped[List['Company']] = relationship(back_populates='license')
