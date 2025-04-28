from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.constants import Title
from src.schemas.types import NameField, OptionalNameField, PhoneNumberField


class AdminBaseSchema(BaseModel):
    """Базовая схема администратора.

    Определяет общие поля администратора.
    Поля:
        name: Имя администратора.
        surname: Фамилия администратора.
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
    """

    name: NameField = Field(..., title=Title.NAME_MODERATOR)
    surname: NameField = Field(..., title=Title.SURNAME_MODERATOR)
    patronymic: OptionalNameField = Field(None, title=Title.PATRONYMIC_MODERATOR)
    phone_number: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_MODERATOR)

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

    email: EmailStr = Field(..., title=Title.EMAIL_USER)
    password: str = Field(..., title=Title.PASSWORD_USER)

class AdminUpdateSchema(AdminBaseSchema):
    """Схема для обновления администратора.

    Поля:
        name: Имя администратора (опционально).
        surname: Фамилия администратора (опционально).
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
    """

    name: OptionalNameField = Field(None, title=Title.NAME_MODERATOR)
    surname: OptionalNameField = Field(None, title=Title.SURNAME_MODERATOR)

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

    is_superuser: bool = Field(True, title=Title.IS_SUPERUSER_ADMIN)