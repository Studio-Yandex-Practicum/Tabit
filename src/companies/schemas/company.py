"""
Модуль схем для компании, отдела и сотрудника отдела.
"""

from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.companies.constants import (
    TITLE_LICENSE_ID_COMPANY,
    TITLE_LOGO_COMPANY,
    TITLE_NAME_COMPANY,
    TITLE_NAME_DEPARTMENT,
    TITLE_SLUG_COMPANY,
    TITLE_SLUG_DEPARTMENT,
    TITLE_START_LICENSE_TIME_COMPANY,
)
from src.companies.schemas.mixins import GetterSlugMixin
from src.companies.validators.company_validators import (
    validate_license_fields,
    validate_name_characters,
    validate_name_surname_unique,
    validate_surname_characters,
)
from src.constants import (
    LENGTH_NAME_COMPANY,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
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
        title=TITLE_NAME_COMPANY,
    )
    logo: Optional[str] = Field(
        None,
        title=TITLE_LOGO_COMPANY,
    )


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

    @model_validator(mode='after')
    def check_license_fields_none(self) -> Self:
        """
        При присвоении лицензии необходимо указать и её начало.
        Нельзя, что бы одно поле было не заполнено.
        """
        validate_license_fields(self.license_id, self.start_license_time)
        return self


class CompanyCreateSchema(GetterSlugMixin, CompanyUpdateSchema):
    """
    Схема для создания компании.
    Параметры:
        name: название компании (обязательно).
        slug: Короткая строка для пути к эндпоинту компании (формируется программно).
    """

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_COMPANY,
    )
    slug: str = Field(..., title=TITLE_SLUG_COMPANY)


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


class CompanyDepartmentUpdateSchema(BaseModel, GetterSlugMixin):
    """
    Схема для обновления данных об отделе.
     Параметры:
        name: новое название отдела (опционально).
        slug: короткая строка для пути к эндпоинту отдела (автозаполнение).
    """

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
