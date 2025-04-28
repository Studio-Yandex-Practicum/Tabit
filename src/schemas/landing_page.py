from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.constants import Title
from src.schemas.types import AddressField, PhoneNumberField, TextField

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)




class LandingPageBaseSchema(BaseModel):
    """Базовая схема для управления контентом лендинга."""

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
    """Схема для создания записи лендинга."""

    model_config = BASE_CONFIG


class LandingPageResponseSchema(LandingPageBaseSchema):
    """Схема для отображения данных лендинга."""

    id: int

    model_config = BASE_CONFIG
