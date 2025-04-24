from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing_extensions import Annotated

from src.schemas.constants import PHONE_REGEX

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

PhoneStr = Annotated[str, StringConstraints(pattern=PHONE_REGEX, max_length=12)]
TextStr = Annotated[str, StringConstraints(max_length=255)]
AddressStr = Annotated[str, StringConstraints(max_length=1000)]

class LandingPageBaseSchema(BaseModel):
    """Базовая схема для управления контентом лендинга."""
    phone_number_1: Optional[PhoneStr] = Field(None, title="Основной номер телефона")
    phone_number_2: Optional[PhoneStr] = Field(None, title="Дополнительный номер телефона 1")
    phone_number_3: Optional[PhoneStr] = Field(None, title="Дополнительный номер телефона 2")
    address: Optional[AddressStr] = Field(None, title="Адрес")
    email: Optional[EmailStr] = Field(None, title="Email")
    whatsapp: Optional[TextStr] = Field(None, title="WhatsApp")
    telegram: Optional[TextStr] = Field(None, title="Telegram")
    vk: Optional[TextStr] = Field(None, title="VK")
    price_1: Optional[TextStr] = Field(None, title="Цена 1")
    price_2: Optional[TextStr] = Field(None, title="Цена 2")

    model_config = BASE_CONFIG

class LandingPageCreateSchema(LandingPageBaseSchema):
    """Схема для создания записи лендинга."""
    model_config = BASE_CONFIG

class LandingPageResponseSchema(LandingPageBaseSchema):
    """Схема для отображения данных лендинга."""
    id: int

    model_config = BASE_CONFIG