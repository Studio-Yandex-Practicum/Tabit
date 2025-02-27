from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.companies.constants import (
    TEST_ERROR_INVALID_CHARACTERS_NAME,
    TEST_ERROR_INVALID_CHARACTERS_SURNAME,
    TEST_ERROR_LICENSE_FIELDS,
    TEST_ERROR_UNIQUE_NAME_SURNAME,
    title_license_id_company,
    title_logo_company,
    title_name_company,
    title_slug_company,
    title_start_license_time,
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


class CompanyUpdateForUserSchema(BaseModel):
    """Схема для частичного изменения компании пользователем-админом."""

    description: Optional[str] = Field(
        None,
        title=title_name_company,
    )
    logo: Optional[str] = Field(
        None,
        title=title_logo_company,
    )


class CompanyUpdateSchema(CompanyUpdateForUserSchema):
    """Схема для частичного изменения компании админом сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title=title_name_company,
    )
    license_id: Optional[int] = Field(
        None,
        title=title_license_id_company,
    )
    start_license_time: Optional[datetime] = Field(
        None,
        title=title_start_license_time,
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
        title=title_name_company,
    )
    slug: str = Field(..., title=title_slug_company)


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
