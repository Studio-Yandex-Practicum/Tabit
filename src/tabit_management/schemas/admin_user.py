from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import Field

from src.constants import MIN_LENGTH_NAME, LENGTH_NAME_USER
from src.tabit_management.constants import (
    title_name_admin,
    title_patronymic_admin,
    title_phone_number_admin,
    title_surname_admin,
)


class AdminReadSchema(BaseUser[UUID]):
    """Схема администратора сервиса для ответов."""

    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_superuser: bool


class AdminCreateSchema(BaseUserCreate):
    """Схема для создание администратора сервиса."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_admin,
    )
    surname: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_admin,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_patronymic_admin,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_phone_number_admin,
    )


class AdminUpdateSchema(BaseUserUpdate):
    """Схема для изменение данных администратора сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_admin,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_admin,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_patronymic_admin,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_phone_number_admin,
    )
