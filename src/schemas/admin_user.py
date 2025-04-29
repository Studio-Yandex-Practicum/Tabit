from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.annotations import NameField, OptionalNameField, PhoneNumberField
from src.schemas.constants import Title


class AdminBaseSchema(BaseModel):
    """
    Базовая схема администратора.

    Определяет общие поля для схем администраторов.

    Атрибуты:
        name (str): Имя администратора.
        surname (str): Фамилия администратора.
        patronymic (Optional[str]): Отчество администратора.
        phone_number (Optional[str]): Номер телефона администратора.
    """

    name: NameField = Field(..., title=Title.NAME_MODERATOR)
    surname: NameField = Field(..., title=Title.SURNAME_MODERATOR)
    patronymic: OptionalNameField = Field(None, title=Title.PATRONYMIC_MODERATOR)
    phone_number: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_MODERATOR)

    model_config = ConfigDict(extra='forbid')


class AdminReadSchema(CreateUpdateDictModel):
    """
    Схема администратора для ответа.

    Используется для возврата данных об администраторе в API.

    Атрибуты:
        id (UUID): Идентификатор администратора.
        email (EmailStr): Электронная почта администратора.
        name (str): Имя администратора.
        surname (str): Фамилия администратора.
        patronymic (Optional[str]): Отчество администратора.
        phone_number (Optional[str]): Номер телефона администратора.
        created_at (datetime): Время создания записи.
        updated_at (datetime): Время последнего обновления записи.
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
    """
    Схема для создания администратора.

    Используется для создания нового администратора через API.

    Атрибуты:
        email (EmailStr): Электронная почта администратора.
        password (str): Пароль администратора.
        name (str): Имя администратора.
        surname (str): Фамилия администратора.
        patronymic (Optional[str]): Отчество администратора.
        phone_number (Optional[str]): Номер телефона администратора.
    """

    email: EmailStr = Field(..., title=Title.EMAIL_USER)
    password: str = Field(..., title=Title.PASSWORD_USER)


class AdminUpdateSchema(AdminBaseSchema):
    """
    Схема для обновления администратора.

    Используется для частичного обновления данных администратора через API.

    Атрибуты:
        name (Optional[str]): Имя администратора.
        surname (Optional[str]): Фамилия администратора.
        patronymic (Optional[str]): Отчество администратора.
        phone_number (Optional[str]): Номер телефона администратора.
    """

    name: OptionalNameField = Field(None, title=Title.NAME_MODERATOR)
    surname: OptionalNameField = Field(None, title=Title.SURNAME_MODERATOR)


class AdminCreateFirstSchema(AdminCreateSchema):
    """
    Схема для создания первого суперпользователя.

    Используется для создания суперпользователя с повышенными привилегиями.

    Атрибуты:
        email (EmailStr): Электронная почта суперпользователя.
        password (str): Пароль суперпользователя.
        name (str): Имя суперпользователя.
        surname (str): Фамилия суперпользователя.
        patronymic (Optional[str]): Отчество суперпользователя.
        phone_number (Optional[str]): Номер телефона суперпользователя.
        is_superuser (bool): Флаг суперпользователя (по умолчанию True).
    """

    is_superuser: bool = Field(True, title=Title.IS_SUPERUSER_ADMIN)
