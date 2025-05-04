from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models import CompanyUserRole
from src.schemas import UserSchemaMixin
from src.schemas.annotations import (
    AvatarLinkField,
    NameField,
    OptionalNameField,
    PhoneNumberField,
    TelegramUsernameField,
)
from src.schemas.constants import TitleConstants


class GetterSlugMixin:
    """
    Миксин для генерации поля slug.

    Формирует поле `slug` на основе значения поля `name`.

    Валидаторы:
        get_slug: Генерирует slug из имени, если данные представлены в виде словаря.
    """

    @model_validator(mode='before')
    @classmethod
    def get_slug(cls, data: Any) -> Any:
        """Формирует `slug` на основе `name`."""
        # TODO: реализовать нормальное создание slug
        # TODO: проверить уникальность slug
        if isinstance(data, dict):
            data['slug'] = data['name']
        return data


class UserReadSchema(BaseUser[UUID]):
    """
    Схема пользователя сервиса для ответов.

    Используется для возврата данных о пользователе через API.

    Атрибуты:
        id (UUID): Идентификатор пользователя.
        email (str): Электронная почта.
        name (str): Имя пользователя.
        surname (str): Фамилия пользователя.
        patronymic (Optional[str]): Отчество пользователя.
        phone_number (Optional[str]): Номер телефона.
        is_active (bool): Активность пользователя.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        role (str): Роль в компании.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        company_id (int): Идентификатор компании.
        current_department_id (Optional[int]): Идентификатор текущего отдела.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        department_transition_date (Optional[date]): Дата перехода в отдел.
        employee_position (Optional[str]): Должность.
        created_at (Optional[datetime]): Время создания записи.
        updated_at (Optional[datetime]): Время последнего обновления записи.
    """

    name: str = Field(..., title=TitleConstants.NAME_USER)
    surname: str = Field(..., title=TitleConstants.SURNAME_USER)
    patronymic: Optional[str] = Field(None, title=TitleConstants.PATRONYMIC_USER)
    phone_number: Optional[str] = Field(None, title=TitleConstants.PHONE_NUMBER_USER)
    is_active: bool = Field(..., title=TitleConstants.IS_ACTIVE_USER)
    birthday: Optional[date] = Field(None, title=TitleConstants.BIRTHDAY_USER)
    telegram_username: Optional[str] = Field(None, title=TitleConstants.TELEGRAM_USERNAME)
    role: str = Field(..., title=TitleConstants.ROLE_USER)
    start_date_employment: Optional[date] = Field(
        None, title=TitleConstants.START_DATE_EMPLOYMENT_USER
    )
    end_date_employment: Optional[date] = Field(
        None, title=TitleConstants.END_DATE_EMPLOYMENT_USER
    )
    avatar_link: Optional[str] = Field(None, title=TitleConstants.AVATAR_LINK_USER)
    company_id: int = Field(..., title=TitleConstants.COMPANY_ID_USER)
    current_department_id: Optional[int] = Field(
        None, title=TitleConstants.CURRENT_DEPARTMENT_ID_USER
    )
    previous_department_id: Optional[int] = Field(
        None, title=TitleConstants.PREVIOUS_DEPARTMENT_ID_USER
    )
    department_transition_date: Optional[date] = Field(
        None, title=TitleConstants.DEPARTMENT_TRANSITION_DATE_USER
    )
    employee_position: Optional[str] = Field(None, title=TitleConstants.EMPLOYEE_POSITION_USER)
    created_at: Optional[datetime] = Field(None, title=TitleConstants.CREATED_AT_USER)
    updated_at: Optional[datetime] = Field(None, title=TitleConstants.UPDATED_AT_USER)

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserSchemaMixin, BaseUserCreate):
    """
    Схема для создания пользователя сервиса.

    Используется для добавления нового пользователя через API.

    Атрибуты:
        name (str): Имя пользователя.
        surname (str): Фамилия пользователя.
        email (str): Электронная почта.
        password (str): Пароль.
        role (CompanyUserRole): Роль в компании (по умолчанию EMPLOYEE).
        company_id (int): Идентификатор компании.
        patronymic (Optional[str]): Отчество пользователя.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        current_department_id (Optional[int]): Идентификатор текущего отдела.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        department_transition_date (Optional[date]): Дата перехода в отдел.
        employee_position (Optional[str]): Должность.
    """

    name: NameField = Field(..., title=TitleConstants.NAME_USER)
    surname: NameField = Field(..., title=TitleConstants.SURNAME_USER)
    role: CompanyUserRole = Field(CompanyUserRole.EMPLOYEE, title=TitleConstants.ROLE_USER)
    company_id: int = Field(..., title=TitleConstants.COMPANY_ID_USER)


class UserUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """
    Схема для изменения данных пользователя сервиса.

    Используется для обновления данных пользователя через API.

    Атрибуты:
        name (Optional[str]): Имя пользователя.
        surname (Optional[str]): Фамилия пользователя.
        email (Optional[str]): Электронная почта.
        password (Optional[str]): Пароль.
        role (Optional[CompanyUserRole]): Роль в компании.
        company_id (Optional[int]): Идентификатор компании.
        patronymic (Optional[str]): Отчество пользователя.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        current_department_id (Optional[int]): Идентификатор текущего отдела.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        department_transition_date (Optional[date]): Дата перехода в отдел.
        employee_position (Optional[str]): Должность.
    """

    name: OptionalNameField = Field(None, title=TitleConstants.NAME_USER)
    surname: OptionalNameField = Field(None, title=TitleConstants.SURNAME_USER)
    role: Optional[CompanyUserRole] = Field(None, title=TitleConstants.ROLE_USER)
    company_id: Optional[int] = Field(None, title=TitleConstants.COMPANY_ID_USER)


class ResetPasswordByAdmin(BaseModel):
    """
    Схема для сброса пароля администратором.

    Используется для задания нового пароля пользователю администратором через API.

    Атрибуты:
        password (str): Новый пароль.
    """

    password: str

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class UserForUserUpdateSchema(BaseModel):
    """
    Схема для обновления данных пользователя сервиса.

    Используется для изменения личных данных пользователя самим пользователем через API.

    Атрибуты:
        name (Optional[str]): Имя пользователя.
        surname (Optional[str]): Фамилия пользователя.
        patronymic (Optional[str]): Отчество пользователя.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        avatar_link (Optional[str]): Ссылка на аватар.
    """

    name: OptionalNameField = Field(None, title=TitleConstants.NAME_USER)
    surname: OptionalNameField = Field(None, title=TitleConstants.SURNAME_USER)
    patronymic: OptionalNameField = Field(None, title=TitleConstants.PATRONYMIC_USER)
    phone_number: PhoneNumberField = Field(None, title=TitleConstants.PHONE_NUMBER_USER)
    birthday: Optional[date] = Field(None, title=TitleConstants.BIRTHDAY_USER)
    telegram_username: TelegramUsernameField = Field(None, title=TitleConstants.TELEGRAM_USERNAME)
    avatar_link: AvatarLinkField = Field(None, title=TitleConstants.AVATAR_LINK_USER)

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
