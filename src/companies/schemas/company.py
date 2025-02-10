from datetime import datetime
from typing import Optional
from typing_extensions import Self

from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator

from src.companies.schemas.mixins import GetterSlugMixin
from src.constants import (LENGTH_NAME_COMPANY, MIN_LENGTH_NAME,
                           LENGTH_NAME_USER, LENGTH_TELEGRAM_USERNAME,
                           MIN_LENGTH_NAME)
from src.users.schemas.user import UserReadSchema
from src.users.constants import (title_telegram_username_user, title_phone_number_user,
                                 title_name_user, title_surname_user)


class CompanyUpdateForUserSchema(BaseModel):
    """Схема для частичного изменения компании пользователем-админом."""

    description: Optional[str] = Field(
        None,
        title='',
    )
    logo: Optional[str] = Field(
        None,
        title='',
    )


class CompanyUpdateSchema(CompanyUpdateForUserSchema):
    """Схема для частичного изменения компании админом сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title='',
    )
    license_id: Optional[int] = Field(
        None,
        title='',
    )
    start_license_time: Optional[datetime] = Field(
        None,
        title='',
    )

    @model_validator(mode='after')
    def check_license_fields_none(self) -> Self:
        """
        При присвоении лицензии необходимо указать и её начало.
        Нельзя, что бы одно поле было не заполнено.
        """
        if not (
            all((self.license_id, self.start_license_time)) or (
                all((not self.license_id, not self.start_license_time))
            )
        ):
            raise ValueError('ДВА ПОЛЯ')
        return self


class CompanyCreateSchema(GetterSlugMixin, CompanyUpdateSchema):
    """Схема для создания компании."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title='',
    )
    slug: str = Field(
        ...,
        title=''
    )


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


class CompanyResponseForUserSchema(UserReadSchema):
    """Схема компании для ответов пользователям."""

    pass


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
    question: str
    # TODO: Обдумать. Скорее всего надо будет реализовать ограничение на количество символов.
    # Схема на данный момент является по большей части заглушкой.

    class Config:
        from_attributes = True
