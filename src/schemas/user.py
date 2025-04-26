from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field

from src.models import CompanyUserRole
from src.schemas import UserSchemaMixin
from src.schemas.constants import Length, Title


class UserReadSchema(BaseUser[UUID]):
    """Схема пользователя сервиса для ответов."""

    name: str = Field(..., title=Title.NAME_USER)
    surname: str = Field(..., title=Title.SURNAME_USER)
    patronymic: Optional[str] = Field(None, title=Title.PATRONYMIC_USER)
    phone_number: Optional[str] = Field(None, title=Title.PHONE_NUMBER_USER)
    is_active: bool = Field(..., title=Title.IS_ACTIVE_USER)
    birthday: Optional[date] = Field(None, title=Title.BIRTHDAY_USER)
    telegram_username: Optional[str] = Field(None, title=Title.TELEGRAM_USERNAME)
    role: str = Field(..., title=Title.ROLE_USER)
    start_date_employment: Optional[date] = Field(None, title=Title.START_DATE_EMPLOYMENT_USER)
    end_date_employment: Optional[date] = Field(None, title=Title.END_DATE_EMPLOYMENT_USER)
    avatar_link: Optional[str] = Field(None, title=Title.AVATAR_LINK_USER)
    company_id: int = Field(..., title=Title.COMPANY_ID_USER)
    current_department_id: Optional[int] = Field(None, title=Title.CURRENT_DEPARTMENT_ID_USER)
    previous_department_id: Optional[int] = Field(None, title=Title.PREVIOUS_DEPARTMENT_ID_USER)
    department_transition_date: Optional[date] = Field(
        None, title=Title.DEPARTMENT_TRANSITION_DATE_USER
    )
    employee_position: Optional[str] = Field(None, title=Title.EMPLOYEE_POSITION_USER)
    created_at: Optional[datetime] = Field(None, title=Title.CREATED_AT_USER)
    updated_at: Optional[datetime] = Field(None, title=Title.UPDATED_AT_USER)
    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserSchemaMixin, BaseUserCreate):
    """Схема для создание пользователя сервиса."""

    name: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_USER,
    )
    surname: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_USER,
    )
    role: CompanyUserRole = Field(
        CompanyUserRole.EMPLOYEE,
        title=Title.ROLE_USER,
    )
    company_id: int = Field(
        ...,
        title=Title.COMPANY_ID_USER,
    )


class UserUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """Схема для изменение данных пользователя сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_USER,
    )
    surname: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_USER,
    )
    role: Optional[CompanyUserRole] = Field(
        None,
        title=Title.ROLE_USER,
    )
    company_id: Optional[int] = Field(
        None,
        title=Title.COMPANY_ID_USER,
    )


class ResetPasswordByAdmin(BaseModel):
    """Схема для сброса пароля админа."""

    password: str
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class UserForUserUpdateSchema(BaseModel):
    """Схема пользователя сервиса для ответов."""

    name: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_USER,
    )
    surname: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_USER,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PATRONYMIC_USER,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PHONE_NUMBER_USER,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=Title.BIRTHDAY_USER,
    )
    telegram_username: Optional[str] = Field(
        None,
        min_length=Length.MIN_TELEGRAMM_USERNAME,
        max_length=Length.MAX_TELEGRAM_USERNAME,
        title=Title.TELEGRAM_USERNAME,
    )
    # TODO: добавить avatar_link

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
