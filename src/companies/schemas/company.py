"""
Модуль схем для компании, отдела и сотрудника отдела.
"""

from datetime import datetime
from typing import Literal, Optional, Self

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
    validate_name_characters,
    validate_name_surname_unique,
    validate_slug,
    validate_string,
    validate_surname_characters,
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
from src.users.schemas import UserUpdateSchema


class CompanyUpdateForUserSchema(BaseModel):
    """
    Схема для частичного изменения компании пользователем-админом.
    Параметры:
        description: новое описание компании (опционально).
        logo: логотип (опционально).
    """

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
        """Проверяет поле description на наличие пробелов в начале или конце."""
        return validate_string(value)


class CompanyUpdateSchema(CompanyUpdateForUserSchema):
    """
    Схема для частичного изменения компании админом сервиса.
    Параметры:
        name: новое название компании (опционально).
        license_id: номер лицензии (опционально).
        start_license_time: дата начала лицензии (опционально).
    """

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
        """Проверяет поле name на наличие пробелов в начале или конце."""
        return validate_string(value)

    @model_validator(mode='after')
    def validate_license_fields(self) -> Self:
        """Проверяет корректность заполнения полей лицензии."""
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
    """
    Схема компании для ответов админам сервиса.
    Параметры:
        id: идентификатор компании (обязательно).
        name: название компании (обязательно).
        description: Описание компании (опционально).
        logo: логотип (опционально).
        license_id: номер лицензии (опционально).
        max_admins_count: максимальное кол-во администраторов (обязательно).
        max_employees_count: максимальное кол-во сотрудников (обязательно)
        start_license_time: дата начала лицензии (опционально).
        end_license_time: дата окончания действия лицензии (опционально).
        is_active: bool - активна ли лицензия (обязательно).
        slug: короткая строка для пути к эндпоинту компании (автозаполнение).
        created_at: дата создания записи в таблице (автозаполнение).
        updated_at: дата изменения записи в таблице (автозаполнение).
    """

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
    """
    Схема для создания отдела.
     Параметры:
        name: название отдела (обязательно).
    """

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_DEPARTMENT,
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyDepartmentResponseSchema(CompanyDepartmentCreateSchema):
    """
    Схема для получения данных отдела.
    Параметры:
        id: идентификатор отдела (обязательно).
        name: название отдела (обязательно).
        slug: короткая строка для пути к эндпоинту отдела (автозаполнение).
        company_id: идентификатор компании (автозаполнение).
    """

    id: int
    name: str
    slug: str
    company_id: int


class CompanyEmployeeUpdateSchema(UserUpdateSchema):
    """Схема для изменения данных сотрудника компании админом компании."""

    @model_validator(mode='after')
    def validate_fields(self) -> Self:
        """Валидатор полей схемы."""
        validate_name_surname_unique(self.name, self.surname)
        validate_name_characters(self.name)
        validate_surname_characters(self.surname)
        return self


class UserCompanyUpdateSchema(BaseModel):
    """
    Схема для редактирования пользователем компании своего профиля.
     Параметры:
        name: новое имя сотрудника (опционально).
        surname: новая фамилия сотрудника (опционально).
        phone_number: новый номер телефона сотрудника (опционально).
        email: новый email сотрудника (опционально).
        telegram_username: новое имя в Телеграме сотрудника (опционально).
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
    def validate_fields(self) -> Self:
        """Валидатор полей схемы."""
        validate_name_surname_unique(self.name, self.surname)
        validate_name_characters(self.name)
        validate_surname_characters(self.surname)
        return self
