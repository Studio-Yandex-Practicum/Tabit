from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import Field

from src.constants import MIN_LENGTH_NAME, LENGTH_NAME_USER
from src.tabit_management.constants import (
    TITLE_NAME_ADMIN,
    TITLE_PATRONYMIC_ADMIN,
    TITLE_PHONE_NUMBER_ADMIN,
    TITLE_SURNAME_ADMIN,
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
        title=TITLE_NAME_ADMIN,
    )
    surname: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_SURNAME_ADMIN,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PATRONYMIC_ADMIN,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PHONE_NUMBER_ADMIN,
    )
    # password: str = Field(exclude=True)
    # hashed_password: str


class AdminUpdateSchema(BaseUserUpdate):
    """Схема для изменение данных администратора сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_NAME_ADMIN,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_SURNAME_ADMIN,
    )
    patronymic: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PATRONYMIC_ADMIN,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PHONE_NUMBER_ADMIN,
    )
