from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from src.schemas.constants import (
    LENGTH_NAME_USER,
    MIN_LENGTH_NAME,
    TITLE_EMAIL,
    TITLE_IS_SUPERUSER_ADMIN,
    TITLE_NAME_MODERATOR,
    TITLE_PASSWORD,
    TITLE_PATRONYMIC_MODERATOR,
    TITLE_PHONE_NUMBER_MODERATOR,
    TITLE_SURNAME_MODERATOR,
)

# Типизация для повторяющихся полей
NameField = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_USER
    ),
]
OptionalNameField = Annotated[
    Optional[str],
    StringConstraints(
        strip_whitespace=True, min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_USER
    ),
]


class AdminBaseSchema(BaseModel):
    """Базовая схема администратора.

    Определяет общие поля администратора.
    Поля:
        name: Имя администратора.
        surname: Фамилия администратора.
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
    """

    name: NameField = Field(..., title=TITLE_NAME_MODERATOR)
    surname: NameField = Field(..., title=TITLE_SURNAME_MODERATOR)
    patronymic: OptionalNameField = Field(None, title=TITLE_PATRONYMIC_MODERATOR)
    phone_number: OptionalNameField = Field(None, title=TITLE_PHONE_NUMBER_MODERATOR)

    model_config = ConfigDict(extra='forbid')


class AdminReadSchema(CreateUpdateDictModel):
    """Схема администратора для ответа.

    Поля:
        id: UUID администратора.
        email: Электронная почта.
        name: Имя администратора.
        surname: Фамилия администратора.
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: UUID
    email: EmailStr
    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminCreateSchema(CreateUpdateDictModel, AdminBaseSchema):
    """Схема для создания администратора.

    Поля:
        email: Электронная почта (обязательно).
        password: Пароль (обязательно).
        name: Имя администратора.
        surname: Фамилия администратора.
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
    """

    email: EmailStr = Field(..., title=TITLE_EMAIL)
    password: str = Field(..., title=TITLE_PASSWORD)


class AdminUpdateSchema(AdminBaseSchema):
    """Схема для обновления администратора.

    Поля:
        name: Имя администратора (опционально).
        surname: Фамилия администратора (опционально).
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
    """

    name: OptionalNameField = Field(None, title=TITLE_NAME_MODERATOR)
    surname: OptionalNameField = Field(None, title=TITLE_SURNAME_MODERATOR)


class AdminCreateFirstSchema(AdminCreateSchema):
    """Схема для создания первого суперпользователя.

    Поля:
        email: Электронная почта (обязательно).
        password: Пароль (обязательно).
        name: Имя администратора.
        surname: Фамилия администратора.
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        is_superuser: Флаг суперпользователя (по умолчанию True).
    """

    is_superuser: bool = Field(True, title=TITLE_IS_SUPERUSER_ADMIN)
