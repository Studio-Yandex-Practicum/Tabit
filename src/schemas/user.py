from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field

from src.models import CompanyUserRole
from src.schemas import UserSchemaMixin
from src.schemas.constants import LengthConstants, TitleConstants


class UserReadSchema(BaseUser[UUID]):
    """Схема пользователя сервиса для ответов."""

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
    """Схема для создание пользователя сервиса."""

    name: str = Field(
        ...,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.NAME_USER,
    )
    surname: str = Field(
        ...,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.SURNAME_USER,
    )
    role: CompanyUserRole = Field(
        CompanyUserRole.EMPLOYEE,
        title=TitleConstants.ROLE_USER,
    )
    company_id: int = Field(
        ...,
        title=TitleConstants.COMPANY_ID_USER,
    )


class UserUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """Схема для изменение данных пользователя сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.NAME_USER,
    )
    surname: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.SURNAME_USER,
    )
    role: Optional[CompanyUserRole] = Field(
        None,
        title=TitleConstants.ROLE_USER,
    )
    company_id: Optional[int] = Field(
        None,
        title=TitleConstants.COMPANY_ID_USER,
    )


class ResetPasswordByAdmin(BaseModel):
    """Схема для сброса пароля админа."""

    password: str
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class UserForUserUpdateSchema(BaseModel):
    """Схема пользователя сервиса для ответов."""

    name: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.NAME_USER,
    )
    surname: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.SURNAME_USER,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.PATRONYMIC_USER,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.PHONE_NUMBER_USER,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TitleConstants.BIRTHDAY_USER,
    )
    telegram_username: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_TELEGRAMM_USERNAME,
        max_length=LengthConstants.MAX_TELEGRAM_USERNAME,
        title=TitleConstants.TELEGRAM_USERNAME,
    )
    # TODO: добавить avatar_link

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
