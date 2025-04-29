from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.annotations import AddressField, PhoneNumberField, TextField
from src.schemas.constants import Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class LandingPageBaseSchema(BaseModel):
    """
    Базовая схема для управления контентом лендинга.

    Определяет общие поля для схем лендинга.

    Атрибуты:
        phone_number_1 (Optional[str]): Первый номер телефона.
        phone_number_2 (Optional[str]): Второй номер телефона.
        phone_number_3 (Optional[str]): Третий номер телефона.
        address (Optional[str]): Адрес компании.
        email (Optional[EmailStr]): Электронная почта.
        whatsapp (Optional[str]): Имя пользователя WhatsApp.
        telegram (Optional[str]): Имя пользователя Telegram.
        vk (Optional[str]): Имя пользователя ВКонтакте.
        price_1 (Optional[str]): Первая цена лицензии.
        price_2 (Optional[str]): Вторая цена лицензии.
    """

    phone_number_1: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    phone_number_2: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    phone_number_3: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    address: Optional[AddressField] = Field(None, title=Title.NAME_COMPANY)
    email: Optional[EmailStr] = Field(None, title=Title.EMAIL_USER)
    whatsapp: Optional[TextField] = Field(None, title=Title.WHATSAPP_USERNAME)
    telegram: Optional[TextField] = Field(None, title=Title.TELEGRAM_USERNAME)
    vk: Optional[TextField] = Field(None, title=Title.NAME_USER)
    price_1: Optional[TextField] = Field(None, title=Title.NAME_LICENSE)
    price_2: Optional[TextField] = Field(None, title=Title.NAME_LICENSE)

    model_config = BASE_CONFIG


class LandingPageCreateSchema(LandingPageBaseSchema):
    """
    Схема для создания записи лендинга.

    Используется для добавления новой записи контента лендинга через API.

    Атрибуты:
        phone_number_1 (Optional[str]): Первый номер телефона.
        phone_number_2 (Optional[str]): Второй номер телефона.
        phone_number_3 (Optional[str]): Третий номер телефона.
        address (Optional[str]): Адрес компании.
        email (Optional[EmailStr]): Электронная почта.
        whatsapp (Optional[str]): Имя пользователя WhatsApp.
        telegram (Optional[str]): Имя пользователя Telegram.
        vk (Optional[str]): Имя пользователя ВКонтакте.
        price_1 (Optional[str]): Первая цена лицензии.
        price_2 (Optional[str]): Вторая цена лицензии.
    """

    model_config = BASE_CONFIG


class LandingPageResponseSchema(LandingPageBaseSchema):
    """
    Схема для отображения данных лендинга.

    Используется для возврата данных о контенте лендинга через API.

    Атрибуты:
        id (int): Идентификатор записи лендинга.
        phone_number_1 (Optional[str]): Первый номер телефона.
        phone_number_2 (Optional[str]): Второй номер телефона.
        phone_number_3 (Optional[str]): Третий номер телефона.
        address (Optional[str]): Адрес компании.
        email (Optional[EmailStr]): Электронная почта.
        whatsapp (Optional[str]): Имя пользователя WhatsApp.
        telegram (Optional[str]): Имя пользователя Telegram.
        vk (Optional[str]): Имя пользователя ВКонтакте.
        price_1 (Optional[str]): Первая цена лицензии.
        price_2 (Optional[str]): Вторая цена лицензии.
    """

    id: int

    model_config = BASE_CONFIG
