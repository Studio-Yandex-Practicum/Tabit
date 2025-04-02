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
    """
    Параметры:
        id: Идентификационный номер пользователя - UUID.
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        birthday: День рождение пользователя.
        telegram_username: Имя пользователя в Telegram.
        role: Роль пользователя компании.
        phone_number: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        start_date_employment: Дата начало работы сотрудника в компании.
        end_date_employment: Дата конца работы сотрудника в компании.
        hashed_password: Хэш пароля пользователя.
        is_active: bool - активен ли пользователь.
        is_superuser: bool - суперюзер ли пользователь.
        is_verified: bool - проверен ли пользователь.
        avatar_link: Ссылка на аватар пользователя.
        company_id: id компании, в которой работает пользователь.
        supervisor: начальник отдела, за которым закреплен (может быть True или None);
        current_department_id: id отдела, в котором работает пользователь.
        last_department_id: id отдела, в котором работал пользователь до этого.
        department_transition_date: Последняя дата перехода из одного отдела в другой.
        employee_position: Позиция в коллективе, указывается админом компании.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

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

    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        title='Базовая схема администратора',
        description='Базовая схема администратора сервиса',
    )


class AdminReadSchema(CreateUpdateDictModel):
    """
    Параметры:
        id: Идентификационный номер пользователя - UUID.
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        phone_number: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.
    """

    id: UUID
    email: EmailStr
    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема админа',
        description='Схема администратора сервиса для ответов',
    )


class AdminCreateSchema(CreateUpdateDictModel, BaseAdminSchema):
    """
    Параметры:
        name: Имя пользователя.
        surname: Фамилия пользователя.
        phone_number: Номер телефона пользователя.
        email: Адрес электронной почты пользователя.
        password: Пароль пользователя.
    """

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

    model_config = ConfigDict(
        title='Схема создания админа',
        description='Схема для создание администратора сервиса'
    )


class AdminUpdateSchema(BaseAdminSchema, BaseModel):
    """
    Параметры:
        name: Имя пользователя.
        surname: Фамилия пользователя.
    """

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

    model_config = ConfigDict(
        title='Схема изменения данных админа',
        description='Схема для изменение данных администратора сервиса'
    )


class AdminCreateFirstSchema(AdminCreateSchema):
    """
    Параметры:
        is_superuser: суперюзер ли пользователь.
    """

    is_superuser: bool = Field(
        True,
        title=TITLE_IS_SUPERUSER_ADMIN,
    )

    model_config = ConfigDict(
        title='Схема создания суперюзера',
        description='Схема для создание первого администратора-суперпользователя сервиса'
    )
