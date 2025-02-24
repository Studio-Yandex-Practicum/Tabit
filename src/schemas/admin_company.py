from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.core.constants.common import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
    MIN_LENGTH_NAME,
)
from src.core.constants.user import (
    TITLE_AVATAR_LINK_USER,
    TITLE_BIRTHDAY_USER,
    TITLE_COMPANY_ID_USER,
    TITLE_CURRENT_DEPARTMENT_ID_USER,
    TITLE_DEPARTMENT_TRANSITION_DATE_USER,
    TITLE_EMPLOYEE_POSITION_USER,
    TITLE_END_DATE_EMPLOYMENT_USER,
    TITLE_LAST_DEPARTMENT_ID_USER,
    TITLE_NAME_USER,
    TITLE_PATRONYMIC_USER,
    TITLE_PHONE_NUMBER_USER,
    TITLE_START_DATE_EMPLOYMENT_USER,
    TITLE_SURNAME_USER,
    TITLE_TELEGRAM_USERNAME_USER,
)
from src.models import RoleUserTabit


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
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PATRONYMIC_USER,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PHONE_NUMBER_USER,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_BIRTHDAY_USER,
    )
    telegram_username: Optional[str] = Field(
        None,
        max_length=LENGTH_TELEGRAM_USERNAME,
        title=TITLE_TELEGRAM_USERNAME_USER,
    )
    start_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_START_DATE_EMPLOYMENT_USER,
    )
    end_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_END_DATE_EMPLOYMENT_USER,
    )
    avatar_link: Optional[str] = Field(
        None,
        max_length=LENGTH_FILE_LINK,
        title=TITLE_AVATAR_LINK_USER,
    )
    current_department_id: Optional[int] = Field(
        None,
        title=TITLE_CURRENT_DEPARTMENT_ID_USER,
    )
    last_department_id: Optional[int] = Field(
        None,
        title=TITLE_LAST_DEPARTMENT_ID_USER,
    )
    department_transition_date: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_DEPARTMENT_TRANSITION_DATE_USER,
    )
    employee_position: Optional[str] = Field(
        None,
        title=TITLE_EMPLOYEE_POSITION_USER,
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
        title=TITLE_NAME_USER,
    )
    surname: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_SURNAME_USER,
    )
    role: Literal[RoleUserTabit.ADMIN]
    company_id: int = Field(
        ...,
        title=TITLE_COMPANY_ID_USER,
    )


class CompanyAdminUpdateSchema(CompanyAdminSchemaMixin, BaseUserUpdate):
    """Схема для изменение данных админов от компаний."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_NAME_USER,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_SURNAME_USER,
    )
    role: Literal[RoleUserTabit.ADMIN]
    company_id: Optional[int] = Field(
        None,
        title=TITLE_COMPANY_ID_USER,
    )
