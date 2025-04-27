from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing_extensions import Annotated

from src.schemas.constants import Length, Title, Validation

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)

PhoneStr = Annotated[
    str,
    StringConstraints(
        pattern=Validation.PHONE_NUMBER_PATTERN, max_length=Length.MIN_TELEGRAMM_USERNAME
    ),
]
TextStr = Annotated[str, StringConstraints(max_length=Length.MAX_DESCRIPTION_COMPANY)]
AddressStr = Annotated[str, StringConstraints(max_length=Length.MAX_DESCRIPTION_COMPANY)]


class LandingPageBaseSchema(BaseModel):
    """Базовая схема для управления контентом лендинга."""

    phone_number_1: Optional[PhoneStr] = Field(None, title=Title.PHONE_NUMBER_USER)
    phone_number_2: Optional[PhoneStr] = Field(None, title=Title.PHONE_NUMBER_USER)
    phone_number_3: Optional[PhoneStr] = Field(None, title=Title.PHONE_NUMBER_USER)
    address: Optional[AddressStr] = Field(None, title=Title.NAME_COMPANY)
    email: Optional[EmailStr] = Field(None, title=Title.EMAIL_USER)
    whatsapp: Optional[TextStr] = Field(None, title=Title.TELEGRAM_USERNAME)
    telegram: Optional[TextStr] = Field(None, title=Title.TELEGRAM_USERNAME)
    vk: Optional[TextStr] = Field(None, title=Title.NAME_USER)
    price_1: Optional[TextStr] = Field(None, title=Title.NAME_LICENSE)
    price_2: Optional[TextStr] = Field(None, title=Title.NAME_LICENSE)

    model_config = BASE_CONFIG


class LandingPageCreateSchema(LandingPageBaseSchema):
    """Схема для создания записи лендинга."""

    model_config = BASE_CONFIG


class LandingPageResponseSchema(LandingPageBaseSchema):
    """Схема для отображения данных лендинга."""

    id: int

    model_config = BASE_CONFIG
