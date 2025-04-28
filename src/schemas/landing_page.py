import re
from typing import Optional

from pydantic import BaseModel, field_validator

from src.schemas.constants import Validation


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
        """
        Проверка формата телефонного номера.

        Поддерживаемые форматы:
        - +7 (123) 456-78-90
        - 8(123)4567890
        - 123-45-67
        - (123) 456 78 90
        """
        if v and not re.match(Validation.PHONE_NUMBER_PATTERN, v):
            raise ValueError(
                'Номер телефона должен быть в одном из следующих форматов: '
                ' +7 (123) 456-78-90, 8(123)4567890, 123-45-67, (123) 456 78 90'
            )
        return v

    @field_validator('email')
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Проверка формата email."""
        if v and not re.match(Validation.EMAIL_REGEX, v):
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
