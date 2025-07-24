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

from src.schemas.constants import LengthConstants, MiscConstants, TitleConstants
from src.schemas.user import UserUpdateSchema
from src.schemas.validators.company import (
    check_license_fields_none,
    validate_name_characters,
    validate_slug,
    validate_string,
    validate_surname_characters,
)


class CompanyUpdateForUserSchema(BaseModel):
    """
    Схема для частичного изменения компании пользователем-админом.
    Параметры:
        description: новое описание компании (опционально).
        logo: логотип (опционально).
    """

    description: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_DESCRIPTION,
        max_length=LengthConstants.MAX_DESCRIPTION_COMPANY,
        title=TitleConstants.NAME_COMPANY,
    )
    logo: Optional[str] = Field(
        None,
        title=TitleConstants.LOGO_COMPANY,
    )

    @field_validator('description', mode='after', check_fields=False)
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
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
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME_COMPANY,
        title=TitleConstants.NAME_COMPANY,
    )
    license_id: Optional[int] = Field(
        None,
        title=TitleConstants.LICENSE_ID_COMPANY,
    )
    start_license_time: Optional[datetime] = Field(
        None,
        title=TitleConstants.START_LICENSE_TIME_COMPANY,
    )
    end_license_time: datetime | None = None

    @field_validator('name', mode='after', check_fields=False)
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Проверяет поле name на наличие пробелов в начале или конце."""
        if value is None:
            return value
        return validate_string(value)

    @model_validator(mode='after')
    def validate_license_fields(self) -> Self:
        """Проверяет корректность заполнения полей лицензии."""
        return check_license_fields_none(self)


class CompanyCreateSchema(CompanyUpdateSchema):
    """Схема для создания компании."""

    name: str = Field(
        ...,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME_COMPANY,
        title=TitleConstants.NAME_COMPANY,
    )
    slug: Optional[str] = Field(None, title=TitleConstants.SLUG_COMPANY)
    is_active: Optional[bool] = None

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

    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)

    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)


class CompanyDepartmentUpdateSchema(BaseModel):
    """Схема для обновления данных об отделе."""

    name: str = Field(
        ...,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME_COMPANY,
        title=TitleConstants.NAME_DEPARTMENT,
    )

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class CompanyDepartmentCreateSchema(CompanyDepartmentUpdateSchema):
    """
    Схема для создания отдела.
     Параметры:
        name: название отдела (обязательно).
    """

    name: str = Field(
        ...,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME_COMPANY,
        title=TitleConstants.NAME_DEPARTMENT,
    )

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


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


class CompanyDepartmentResponseSchemaForAdmin(CompanyDepartmentResponseSchema):
    """
    Схема для получения данных отдела.
    Параметры:
        id: идентификатор отдела (обязательно).
        name: название отдела (обязательно).
        slug: короткая строка для пути к эндпоинту отдела (автозаполнение).
        company_id: идентификатор компании (автозаполнение).
        created_at: дата создания отдела.
        updated_at: дата изменения отдела.
    """

    created_at: datetime
    updated_at: datetime


class CompanyEmployeeUpdateSchema(UserUpdateSchema):
    """Схема для изменения данных сотрудника компании админом компании."""

    @model_validator(mode='after')
    def validate_fields(self) -> Self:
        """Валидатор полей схемы."""
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
    phone_number: Optional[PhoneNumber] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.PHONE_NUMBER_USER,
    )
    email: Optional[EmailStr]
    telegram_username: Optional[str] = Field(
        None,
        max_length=LengthConstants.MAX_TELEGRAM_USERNAME,
        title=TitleConstants.TELEGRAM_USERNAME,
    )

    @model_validator(mode='after')
    def validate_fields(self) -> Self:
        """Валидатор полей схемы."""
        validate_name_characters(self.name)
        validate_surname_characters(self.surname)
        return self


class CompanyFeedbackCreateShema(BaseModel):
    """Схема для создания пользователем компании обратной связи."""

    question: str = Field(..., title='Задать вопрос для обратной связи')
    # TODO: Обдумать. Скорее всего надо будет реализовать ограничение на количество символов.
    # Схема на данный момент является по большей части заглушкой.

    class Config:
        from_attributes = True
