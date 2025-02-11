from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.constants import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
    MIN_LENGTH_NAME,
)
from src.users.constants import (
    title_avatar_link_user,
    title_birthday_user,
    title_company_id_user,
    title_current_department_id_user,
    title_department_transition_date_user,
    title_employee_position_user,
    title_end_date_employment_user,
    title_last_department_id_user,
    title_name_user,
    title_patronymic_user,
    title_phone_number_user,
    title_start_date_employment_user,
    title_surname_user,
    title_telegram_username_user,
)
from src.users.models.enum import RoleUserTabit


class AdminCompanyResponseSchema(BaseModel):
    """Схема компании для ответов админам сервиса."""

    id: int
    name: str
    description: Optional[str]
    logo: Optional[HttpUrl]
    license_id: Optional[int]
    max_admins_count: int
    max_employees_count: int
    start_license_time: Optional[datetime]
    end_license_time: Optional[datetime]
    is_active: bool
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyAdminSchemaMixin:
    """Схема-миксин для админов от компаний."""

    patronymic: Optional[str] = Field(
        None, min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_USER, title=title_patronymic_user
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


class CompanyAdminReadSchema(BaseUser[UUID]):
    """Схема для возврата данных админов от компаний при работе с ними."""

    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    birthday: Optional[date]
    telegram_username: Optional[str]
    role: str
    start_date_employment: Optional[date]
    end_date_employment: Optional[date]
    avatar_link: Optional[str]
    company_id: int
    current_department_id: Optional[int]
    last_department_id: Optional[int]
    department_transition_date: Optional[date]
    employee_position: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CompanyAdminCreateSchema(CompanyAdminSchemaMixin, BaseUserCreate):
    """Схема для создания админов от компаний."""

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
    role: Literal[RoleUserTabit.ADMIN]
    company_id: int = Field(
        ...,
        title=title_company_id_user,
    )


class CompanyAdminUpdateSchema(CompanyAdminSchemaMixin, BaseUserUpdate):
    """Схема для изменение данных админов от компаний."""

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
    role: Literal[RoleUserTabit.ADMIN]
    company_id: Optional[int] = Field(
        None,
        title=title_company_id_user,
    )
