from typing import Optional

from sqlalchemy.orm import Mapped

from src.core.annotations import int_pk
from src.models import BaseTabitModel


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
