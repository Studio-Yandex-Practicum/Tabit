from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, name_field
from src.database.models import BaseTabitModel, BaseUser
from src.tabit_management.constants import DEFAULT_NUMBER_DEY_LICENSE


if TYPE_CHECKING:
    from src.companies.models import Company


class TabitAdminUser(BaseUser):
    """
    Модель пользователей-админов сервиса Tabit.

    Назначение:
        Хранит сведения о админов и модераторов, обслуживающих сервис Tabit.

    Поля:
        id: Идентификационный номер пользователя - UUID.
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        phone_number: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        hashed_password: Хэш пароля пользователя.
        is_active: bool - активен ли пользователь.
        is_superuser: bool - суперюзер ли пользователь.
        is_verified: bool - проверен ли пользователь.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

    pass


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
    name: Mapped[name_field]
    license_term: Mapped[Interval] = mapped_column(
        Interval(day_precision=DEFAULT_NUMBER_DEY_LICENSE)
    )
    max_admins_count: Mapped[int]
    max_employees_count: Mapped[int]

    companies: Mapped[List['Company']] = relationship(back_populates='license')


class LandingPage(BaseTabitModel):
    """
    Модель для хранения общей информации сайта.

    Назначение:
        Хранит сведения контактных телефонах компании, адресе офиса, электронную почту, Вконтакте,
        whatsapp и telegram, а так же прочую информацию.

    Поля:
        id: Идентификатор.
        phone_number_1: Телефонный номер, по которому можно связаться с представителем сервиса.
        phone_number_2: Телефонный номер, по которому можно связаться с представителем сервиса.
        phone_number_3: Телефонный номер, по которому можно связаться с представителем сервиса.
        address: Адрес офиса представителей сервиса.
        email: Электронный адрес представителей сервиса.
        whatsapp: Whatsapp контакт представителей сервиса.
        telegram: Telegram контакт представителей сервиса.
        vk: ВКонтакте контакт представителей сервиса.
        price_1: Цена услуги.
        price_2: Цена услуги.
    """

    id: Mapped[int_pk]
    phone_number_1: Mapped[Optional[str]]
    phone_number_2: Mapped[Optional[str]]
    phone_number_3: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    whatsapp: Mapped[Optional[str]]
    telegram: Mapped[Optional[str]]
    vk: Mapped[Optional[str]]
    price_1: Mapped[Optional[str]]
    price_2: Mapped[Optional[str]]
