from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.constants import LENGTH_NAME_USER, MIN_LENGTH_NAME
from src.tabit_management.constants import (
    TITLE_EMAIL,
    TITLE_IS_SUPERUSER_ADMIN,
    TITLE_NAME_ADMIN,
    TITLE_PASSWORD,
    TITLE_PATRONYMIC_ADMIN,
    TITLE_PHONE_NUMBER_ADMIN,
    TITLE_SURNAME_ADMIN,
)


class BaseAdminSchema:
    """Базовая схема администратора сервиса."""

    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PATRONYMIC_ADMIN,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PHONE_NUMBER_ADMIN,
    )

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class AdminReadSchema(CreateUpdateDictModel):
    """Схема администратора сервиса для ответов."""

    id: UUID
    email: EmailStr
    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminCreateSchema(CreateUpdateDictModel, BaseAdminSchema):
    """Схема для создание администратора сервиса."""

    email: EmailStr = Field(
        ...,
        title=TITLE_EMAIL,
    )
    password: str = Field(
        ...,
        title=TITLE_PASSWORD,
    )

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_NAME_ADMIN,
    )
    surname: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_SURNAME_ADMIN,
    )


class AdminUpdateSchema(BaseAdminSchema, BaseModel):
    """Схема для изменение данных администратора сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_NAME_ADMIN,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_SURNAME_ADMIN,
    )


class AdminCreateFirstSchema(AdminCreateSchema):
    """Схема для создание первого администратора-суперпользователя сервиса."""

    is_superuser: bool = Field(
        True,
        title=TITLE_IS_SUPERUSER_ADMIN,
    )
