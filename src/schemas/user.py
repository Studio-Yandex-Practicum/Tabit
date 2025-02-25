from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field

from src.core.constants.common import (
    LENGTH_NAME_USER,
    MIN_LENGTH_NAME,
)
from src.core.constants.user import (
    TITLE_AVATAR_LINK_USER,
    TITLE_BIRTHDAY_USER,
    TITLE_COMPANY_ID_USER,
    TITLE_CREATED_AT_USER,
    TITLE_CURRENT_DEPARTMENT_ID_USER,
    TITLE_DEPARTMENT_TRANSITION_DATE_USER,
    TITLE_EMPLOYEE_POSITION_USER,
    TITLE_END_DATE_EMPLOYMENT_USER,
    TITLE_IS_ACTIVE_USER,
    TITLE_LAST_DEPARTMENT_ID_USER,
    TITLE_NAME_USER,
    TITLE_PATRONYMIC_USER,
    TITLE_PHONE_NUMBER_USER,
    TITLE_ROLE_USER,
    TITLE_START_DATE_EMPLOYMENT_USER,
    TITLE_SURNAME_USER,
    TITLE_TELEGRAM_USERNAME_USER,
    TITLE_UPDATED_AT_USER,
)
from src.models import RoleUserTabit
from src.schemas import UserSchemaMixin


class UserReadSchema(BaseUser[UUID]):
    """Схема пользователя сервиса для ответов."""

    name: str = Field(..., title=TITLE_NAME_USER)
    surname: str = Field(..., title=TITLE_SURNAME_USER)
    patronymic: Optional[str] = Field(None, title=TITLE_PATRONYMIC_USER)
    phone_number: Optional[str] = Field(None, title=TITLE_PHONE_NUMBER_USER)
    is_active: bool = Field(..., title=TITLE_IS_ACTIVE_USER)
    birthday: Optional[date] = Field(None, title=TITLE_BIRTHDAY_USER)
    telegram_username: Optional[str] = Field(None, title=TITLE_TELEGRAM_USERNAME_USER)
    role: str = Field(..., title=TITLE_ROLE_USER)
    start_date_employment: Optional[date] = Field(None, title=TITLE_START_DATE_EMPLOYMENT_USER)
    end_date_employment: Optional[date] = Field(None, title=TITLE_END_DATE_EMPLOYMENT_USER)
    avatar_link: Optional[str] = Field(None, title=TITLE_AVATAR_LINK_USER)
    company_id: int = Field(..., title=TITLE_COMPANY_ID_USER)
    current_department_id: Optional[int] = Field(None, title=TITLE_CURRENT_DEPARTMENT_ID_USER)
    last_department_id: Optional[int] = Field(None, title=TITLE_LAST_DEPARTMENT_ID_USER)
    department_transition_date: Optional[date] = Field(
        None, title=TITLE_DEPARTMENT_TRANSITION_DATE_USER
    )
    employee_position: Optional[str] = Field(None, title=TITLE_EMPLOYEE_POSITION_USER)
    created_at: Optional[datetime] = Field(None, title=TITLE_CREATED_AT_USER)
    updated_at: Optional[datetime] = Field(None, title=TITLE_UPDATED_AT_USER)
    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserSchemaMixin, BaseUserCreate):
    """Схема для создание пользователя сервиса."""

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
    role: RoleUserTabit = Field(
        RoleUserTabit.EMPLOYEE,
        title=TITLE_ROLE_USER,
    )
    company_id: int = Field(
        ...,
        title=TITLE_COMPANY_ID_USER,
    )


class UserUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """Схема для изменение данных пользователя сервиса."""

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
    role: Optional[RoleUserTabit] = Field(
        None,
        title=TITLE_ROLE_USER,
    )
    company_id: Optional[int] = Field(
        None,
        title=TITLE_COMPANY_ID_USER,
    )


class ResetPasswordByAdmin(BaseModel):
    """Схема для сброса пароля админа."""

    password: str
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
