from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.constants import Length, Title


class BaseAdminSchema:
    """Базовая схема администратора сервиса."""

    patronymic: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PATRONYMIC_MODERATOR,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PHONE_NUMBER_MODERATOR,
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
        title=Title.EMAIL_USER,
    )
    password: str = Field(
        ...,
        title=Title.PASSWORD_USER,
    )

    name: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_MODERATOR,
    )
    surname: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_MODERATOR,
    )


class AdminUpdateSchema(BaseAdminSchema, BaseModel):
    """Схема для изменение данных администратора сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_MODERATOR,
    )
    surname: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_MODERATOR,
    )


class AdminCreateFirstSchema(AdminCreateSchema):
    """Схема для создание первого администратора-суперпользователя сервиса."""

    is_superuser: bool = Field(
        True,
        title=Title.IS_SUPERUSER_ADMIN,
    )
