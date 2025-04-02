import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

PHONE_REGEX = r'^\+7\d{10}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class LandingPageBaseSchema(BaseModel):
    """
    Параметры:
        phone_number_1: Телефонный номер представителя сервиса(опционально).
        phone_number_2: Телефонный номер представителя сервиса(опционально).
        phone_number_3: Телефонный номер представителя сервиса(опционально).
        address: Адрес офиса представителей сервиса(опционально).
        email: Электронный адрес представителей сервиса(опционально).
        whatsapp: Whatsapp контакт представителей сервиса(опционально).
        telegram: Telegram контакт представителей сервиса(опционально).
        vk: ВКонтакте контакт представителей сервиса(опционально).
        price_1: Цена услуги(опционально).
        price_2: Цена услуги(опционально).
    """

    phone_number_1: Optional[str]
    phone_number_2: Optional[str]
    phone_number_3: Optional[str]
    address: Optional[str]
    email: Optional[str]
    whatsapp: Optional[str]
    telegram: Optional[str]
    vk: Optional[str]
    price_1: Optional[str]
    price_2: Optional[str]

    model_config = ConfigDict(
        title = "Схема управления конетентом",
        description = "Базовая схема для управления контентом лендинга"
    )

    @field_validator('phone_number_1', 'phone_number_2', 'phone_number_3')
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Проверка формата телефонного номера(формат +7xxxxxxxxxx)."""
        if v and not re.match(PHONE_REGEX, v):
            raise ValueError('Номер телефона должен быть в формате: +7xxxxxxxxxx')
        return v

    @field_validator('email')
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Проверка формата email."""
        if v and not re.match(EMAIL_REGEX, v):
            raise ValueError('Некорректный формат email.')
        return v


class LandingPageCreateSchema(LandingPageBaseSchema):
    """Схема для создания записи лендинга."""

    model_config = ConfigDict(
        title = "Схема создания записи",
        description = "Схема для создания записи лендинга"
    )


class LandingPageUpdateSchema(LandingPageBaseSchema):
    """Схема для обновления записи лендинга."""

    model_config = ConfigDict(
        title = "Схема обновления записи",
        description = "Схема для обновления записи лендинга"
    )


class LandingPageResponseSchema(LandingPageBaseSchema):
    """
    Параметры:
        id: Идентефикатор.
    """

    id: int

    model_config = ConfigDict(
        title = "Схема данных лендинга",
        description = "Схема для отображения данных лендинга"
    )
