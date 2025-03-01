"""
Модуль схем для компании, отдела и сотрудника отдела.
"""

from datetime import datetime
from typing import Literal, Optional, Self

from fastapi_users.schemas import BaseUserUpdate
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.companies.constants import (
    FILTER_NAME_DESCRIPTION,
    SORTING_DESCRIPTION,
    TEST_ERROR_INVALID_CHARACTERS_NAME,
    TEST_ERROR_INVALID_CHARACTERS_SURNAME,
    TEST_ERROR_UNIQUE_NAME_SURNAME,
    TITLE_LICENSE_ID_COMPANY,
    TITLE_LOGO_COMPANY,
    TITLE_NAME_COMPANY,
    TITLE_NAME_DEPARTMENT,
    TITLE_SLUG_COMPANY,
    TITLE_SLUG_DEPARTMENT,
    TITLE_START_LICENSE_TIME_COMPANY,
)
from src.companies.validators.company_validators import (
    check_license_fields_none,
    validate_logo,
    validate_slug,
    validate_string,
)
from src.constants import (
    LENGTH_DESCRIPTION_COMPANY,
    LENGTH_NAME_COMPANY,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
    MIN_DESCRIPTION_NAME,
    MIN_LENGTH_NAME,
)
from src.users.constants import (
    title_name_user,
    title_phone_number_user,
    title_surname_user,
    title_telegram_username_user,
)
from src.users.schemas import UserSchemaMixin


class CompanyUpdateForUserSchema(BaseModel):
    """Схема для частичного изменения компании пользователем-админом."""

    description: Optional[str] = Field(
        None,
        min_length=MIN_DESCRIPTION_NAME,
        max_length=LENGTH_DESCRIPTION_COMPANY,
        title=TITLE_NAME_COMPANY,
    )
    logo: Optional[str] = Field(
        None,
        title=TITLE_LOGO_COMPANY,
    )

    @field_validator('logo')
    @classmethod
    def validate_logo_field(cls, logo: Optional[str]) -> Optional[str]:
        """Проверяет, что logo является корректным URL-адресом."""
        return validate_logo(logo)

    @field_validator('description', mode='after', check_fields=False)
    @classmethod
    def validate_description(cls, value: str):
        return validate_string(value)


class CompanyUpdateSchema(CompanyUpdateForUserSchema):
    """Схема для частичного изменения компании админом сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_COMPANY,
    )
    license_id: Optional[int] = Field(
        None,
        title=TITLE_LICENSE_ID_COMPANY,
    )
    start_license_time: Optional[datetime] = Field(
        None,
        title=TITLE_START_LICENSE_TIME_COMPANY,
    )
    end_license_time: datetime | None = None

    @field_validator('name', mode='after', check_fields=False)
    @classmethod
    def validate_name(cls, value: str):
        return validate_string(value)

    @model_validator(mode='after')
    def validate_license_fields(self) -> Self:
        return check_license_fields_none(self)


class CompanyCreateSchema(CompanyUpdateSchema):
    """Схема для создания компании."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_COMPANY,
    )
    slug: Optional[str] = Field(None, title=TITLE_SLUG_COMPANY)

    @field_validator('slug')
    @classmethod
    def check_slug(cls, slug: Optional[str]) -> Optional[str]:
        """Вызывает валидатор slug из модуля validators."""
        return validate_slug(slug)


class CompanyResponseSchema(BaseModel):
    """Схема компании для ответов админам сервиса."""

    id: int
    name: str
    description: Optional[str]
    logo: Optional[str]
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


class CompanyTypeFilterSchema(BaseModel):
    """
    Схема фильтрации списка компании с возможностью сортировки.

    Attributes:
        name (Optional[str]): Фильтр по названию компании.
        ordering (Optional[Literal]): Сортировка (по полям name, created_at, updated_at).
    """

    name: Optional[str] = Field(None, description=FILTER_NAME_DESCRIPTION)

    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=SORTING_DESCRIPTION)


class CompanyDepartmentUpdateSchema(BaseModel):
    """Схема для обновления данных об отделе."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_DEPARTMENT,
    )
    slug: Optional[str] = Field(None, title=TITLE_SLUG_DEPARTMENT)

    model_config = ConfigDict(extra='forbid')


class CompanyDepartmentCreateSchema(CompanyDepartmentUpdateSchema):
    """Схема для создания отдела."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_DEPARTMENT,
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyDepartmentResponseSchema(CompanyDepartmentCreateSchema):
    """Схема для получения данных отдела."""

    id: int
    name: str
    slug: str
    company_id: int


class CompanyEmployeeUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """Схема для изменения данных сотрудника компании."""


class UserCompanyUpdateSchema(BaseModel):
    """Схема для редактирования пользователем компании своего профиля."""

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
    phone_number: Optional[PhoneNumber] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_phone_number_user,
    )
    email: Optional[EmailStr]
    telegram_username: Optional[str] = Field(
        None,
        max_length=LENGTH_TELEGRAM_USERNAME,
        title=title_telegram_username_user,
    )

    @model_validator(mode='after')
    def validate_unique_name_surname(self) -> Self:
        if self.name and self.surname and self.name == self.surname:
            raise ValueError(TEST_ERROR_UNIQUE_NAME_SURNAME)
        if self.name and not self.name.isalpha():
            raise ValueError(TEST_ERROR_INVALID_CHARACTERS_NAME)
        if self.surname and not self.surname.isalpha():
            raise ValueError(TEST_ERROR_INVALID_CHARACTERS_SURNAME)
        return self
