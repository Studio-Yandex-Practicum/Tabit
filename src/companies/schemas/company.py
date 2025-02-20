"""
Модуль схем для компании, отдела и сотрудника отдела.
"""

from datetime import datetime
from typing import Optional, Self

from fastapi_users.schemas import BaseUserUpdate
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from src.companies.constants import (
    TEST_ERROR_LICENSE_FIELDS,
    TITLE_LICENSE_ID_COMPANY,
    TITLE_LOGO_COMPANY,
    TITLE_NAME_COMPANY,
    TITLE_NAME_DEPARTMENT,
    TITLE_SLUG_COMPANY,
    TITLE_SLUG_DEPARTMENT,
    TITLE_START_LICENSE_TIME_COMPANY,
)
from src.companies.schemas.mixins import GetterSlugMixin
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
from src.users.schemas import UserSchemaMixin


class CompanyUpdateForUserSchema(BaseModel):
    """Схема для частичного изменения компании пользователем-админом."""

    description: Optional[str] = Field(
        None,
        title=TITLE_NAME_COMPANY,
    )
    logo: Optional[str] = Field(
        None,
        title=TITLE_LOGO_COMPANY,
    )


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

    @model_validator(mode='after')
    def check_license_fields_none(self) -> Self:
        """
        При присвоении лицензии необходимо указать и её начало.
        Нельзя, что бы одно поле было не заполнено.
        """
        if not (
            all((self.license_id, self.start_license_time))
            or (all((not self.license_id, not self.start_license_time)))
        ):
            raise ValueError(TEST_ERROR_LICENSE_FIELDS)
        return self


class CompanyCreateSchema(GetterSlugMixin, CompanyUpdateSchema):
    """Схема для создания компании."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=TITLE_NAME_COMPANY,
    )
    slug: str = Field(..., title=TITLE_SLUG_COMPANY)


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


class CompanyDepartmentUpdateSchema(BaseModel, GetterSlugMixin):
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
    phone_number: Optional[str] = Field(
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


class CompanyFeedbackCreateShema(BaseModel):
    """Схема для создания пользователем компании обратной связи."""

    question: str = Field(..., title='Задать вопрос для обратной связи')
    # TODO: Обдумать. Скорее всего надо будет реализовать ограничение на количество символов.
    # Схема на данный момент является по большей части заглушкой.

    class Config:
        from_attributes = True
