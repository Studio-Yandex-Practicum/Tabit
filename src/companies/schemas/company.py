from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from src.companies.constants import (
    TEST_ERROR_LICENSE_FIELDS,
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
    # TODO: Убрать из схемы атрибут slug. Добавить свойство slug и декорировать его
    # computed_field. Все в миксине.
    # https://docs.pydantic.dev/latest/concepts/fields/#customizing-json-schema:~:text=JSON%20schema%20docs.-,The%20computed_field%20decorator,-%C2%B6
    slug: str = Field(..., title=title_slug_company, exclude=True)


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
