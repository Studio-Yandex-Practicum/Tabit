from pydantic import BaseModel, field_validator
from typing import Optional
import re


PHONE_REGEX = r'^\+7\d{10}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class LandingPageBaseSchema(BaseModel):
    """Базовая схема для управления контентом лендинга."""

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
    pass


class LandingPageUpdateSchema(LandingPageBaseSchema):
    """Схема для обновления записи лендинга."""
    pass


class LandingPageResponseSchema(LandingPageBaseSchema):
    """Схема для отображения данных лендинга."""
    id: int
