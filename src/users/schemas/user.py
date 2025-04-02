from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field

from src.constants import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
    MIN_LENGTH_NAME,
    MIN_LENGTH_TELEGRAM_USERNAME,
)
from src.users.constants import (
    title_avatar_link_user,
    title_birthday_user,
    title_company_id_user,
    title_created_at_user,
    title_current_department_id_user,
    title_department_transition_date_user,
    title_employee_position_user,
    title_end_date_employment_user,
    title_is_active_user,
    title_last_department_id_user,
    title_name_user,
    title_patronymic_user,
    title_phone_number_user,
    title_role_user,
    title_start_date_employment_user,
    title_surname_user,
    title_telegram_username_user,
    title_updated_at_user,
)
from src.users.models.enum import RoleUserTabit


class UserSchemaMixin:
    """Схема-миксин пользователя сервиса."""

    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_patronymic_user,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_phone_number_user,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=title_birthday_user,
    )
    telegram_username: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_TELEGRAM_USERNAME,
        max_length=LENGTH_TELEGRAM_USERNAME,
        title=title_telegram_username_user,
    )
    start_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=title_start_date_employment_user,
    )
    end_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=title_end_date_employment_user,
    )
    avatar_link: Optional[str] = Field(
        None,
        max_length=LENGTH_FILE_LINK,
        title=title_avatar_link_user,
    )
    current_department_id: Optional[int] = Field(
        None,
        title=title_current_department_id_user,
    )
    last_department_id: Optional[int] = Field(
        None,
        title=title_last_department_id_user,
    )
    department_transition_date: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=title_department_transition_date_user,
    )
    employee_position: Optional[str] = Field(
        None,
        title=title_employee_position_user,
    )
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class UserReadSchema(BaseUser[UUID]):
    """
    Параметры:
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        phone_number: Номер телефона пользователя.
        birthday: День рождение пользователя.
        is_active: bool - активен ли пользователь.
        telegram_username: Имя пользователя в Telegram.
        role: Роль пользователя компании.
        start_date_employment: Дата начало работы сотрудника в компании.
        end_date_employment: Дата конца работы сотрудника в компании.
        avatar_link: Ссылка на аватар пользователя.
        company_id: id компании, в которой работает пользователь.
        current_department_id: id отдела, в котором работает пользователь.
        last_department_id: id отдела, в котором работал пользователь до этого.
        department_transition_date: Последняя дата перехода из одного отдела в другой.
        employee_position: Позиция в коллективе, указывается админом компании.
        created_at: Дата создания записи в таблице.
        updated_at: Дата изменения записи в таблице.
    """

    name: str = Field(..., title=title_name_user)
    surname: str = Field(..., title=title_surname_user)
    patronymic: Optional[str] = Field(None, title=title_patronymic_user)
    phone_number: Optional[str] = Field(None, title=title_phone_number_user)
    is_active: bool = Field(..., title=title_is_active_user)
    birthday: Optional[date] = Field(None, title=title_birthday_user)
    telegram_username: Optional[str] = Field(None, title=title_telegram_username_user)
    role: str = Field(..., title=title_role_user)
    start_date_employment: Optional[date] = Field(None, title=title_start_date_employment_user)
    end_date_employment: Optional[date] = Field(None, title=title_end_date_employment_user)
    avatar_link: Optional[str] = Field(None, title=title_avatar_link_user)
    company_id: int = Field(..., title=title_company_id_user)
    current_department_id: Optional[int] = Field(None, title=title_current_department_id_user)
    last_department_id: Optional[int] = Field(None, title=title_last_department_id_user)
    department_transition_date: Optional[date] = Field(
        None, title=title_department_transition_date_user
    )
    employee_position: Optional[str] = Field(None, title=title_employee_position_user)
    created_at: Optional[datetime] = Field(None, title=title_created_at_user)
    updated_at: Optional[datetime] = Field(None, title=title_updated_at_user)

    model_config = ConfigDict(
        from_attributes=True,
        title="Схема пользователя",
        description="Схема пользователя сервиса для ответов"
    )


class UserCreateSchema(UserSchemaMixin, BaseUserCreate):
    """
    Параметры:
        name: Имя пользователя.
        surname: Фамилия пользователя.
        role: Роль пользователя компании.
        company_id: id компании, в которой работает пользователь.
    """

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_user,
    )
    surname: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_user,
    )
    role: RoleUserTabit = Field(
        RoleUserTabit.EMPLOYEE,
        title=title_role_user,
    )
    company_id: int = Field(
        ...,
        title=title_company_id_user,
    )

    model_config = ConfigDict(
        title="Схема создания пользователя",
        description="Схема для создание пользователя сервиса"
    )


class UserUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """
    Параметры:
        name: Имя пользователя.
        surname: Фамилия пользователя.
        role: Роль пользователя компании.
        company_id: id компании, в которой работает пользователь.
    """

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_user,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_user,
    )
    role: Optional[RoleUserTabit] = Field(
        None,
        title=title_role_user,
    )
    company_id: Optional[int] = Field(
        None,
        title=title_company_id_user,
    )

    model_config = ConfigDict(
        title="Схема изменения пользователя",
        description="Схема для изменения данных пользователя сервиса"
    )


class ResetPasswordByAdmin(BaseModel):
    """
    password: Пароль.
    """

    password: str

    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        title="Схема пароля",
        description="Схема для сброса пароля админа"
    )


class UserForUserUpdateSchema(BaseModel):
    """Схема пользователя сервиса для ответов.
    Параметры:
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество пользователя.
        phone_number: Номер телефона пользователя.
        birthday: День рождение пользователя.
        telegram_username: Имя пользователя в Telegram.
        avatar_link: Ссылка на аватар пользователя.
    """

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_user,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_user,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_patronymic_user,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_phone_number_user,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=title_birthday_user,
    )
    telegram_username: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_TELEGRAM_USERNAME,
        max_length=LENGTH_TELEGRAM_USERNAME,
        title=title_telegram_username_user,
    )
    # TODO: добавить avatar_link

    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        title="Схема для ответов",
        description="Схема пользователя сервиса для ответов"
    )
