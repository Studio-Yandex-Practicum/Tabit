from datetime import datetime, timedelta
from re import compile
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.constants import LENGTH_NAME_LICENSE, MIN_LENGTH_NAME, ZERO
from src.tabit_management.constants import (
    DEFAULT_LICENSE_TERM,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    ERROR_FIELD_INTERVAL,
    ERROR_FIELD_START_OR_END_SPACE,
    FILTER_NAME_DESCRIPTION,
    ITEMS_DESCRIPTION,
    MAX_PAGE_SIZE,
    MIN_PAGE_SIZE,
    PAGE_DESCRIPTION,
    PAGE_SIZE_DESCRIPTION,
    SORTING_DESCRIPTION,
    TITLE_LICENSE_TERM,
    TITLE_MAX_ADMINS_COUNT,
    TITLE_MAX_EMPLOYEES_COUNT,
    TITLE_NAME_LICENSE,
    TOTAL_DESCRIPTION,
)


class LicenseTypeBaseSchema(BaseModel):
    """Базовая схема лицензии."""

    @classmethod
    def _validator_field_string(cls, value: str):
        """Проверит строковое поле, чтобы не было пробелов вначале или конце."""
        if value != value.strip():
            raise ValueError(ERROR_FIELD_START_OR_END_SPACE)
        return value

    @classmethod
    def _validator_field_interval(cls, value: int):
        """
        Проверка поля timedelta.
        Проверка происходит до проверки по типу.
        Поле может принимать строку формата "P1D", "P1Y", "P1Y1D", где:
            P - обязательный указатель, ставится в начале строки,
            1D - количество дней, в данном случае: 1 день,
            1Y - количество лет, в данном случае: 1 год.
        """
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if isinstance(value, int):
            return timedelta(days=value)
        if compile(r'^P.*Y$|^P.*D$').match(value):
            return value
        raise ValueError(ERROR_FIELD_INTERVAL)


class LicenseTypeCreateSchema(LicenseTypeBaseSchema):
    """Схема для создания лицензии."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_LICENSE,
        title=TITLE_NAME_LICENSE,
    )
    license_term: timedelta = Field(
        ...,
        ge=timedelta(**DEFAULT_LICENSE_TERM),
        title=TITLE_LICENSE_TERM,
    )
    max_admins_count: int = Field(
        ...,
        gt=ZERO,
        title=TITLE_MAX_ADMINS_COUNT,
    )
    max_employees_count: int = Field(
        ...,
        gt=ZERO,
        title=TITLE_MAX_EMPLOYEES_COUNT,
    )

    @field_validator('name', mode='after')
    @classmethod
    def str_field(cls, value: str):
        return cls._validator_field_string(value)

    @field_validator('license_term', mode='before')
    @classmethod
    def interval_field(cls, value: int):
        return cls._validator_field_interval(value)


class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """Схема для частичного изменения лицензии."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_LICENSE,
        title=TITLE_NAME_LICENSE,
    )
    license_term: Optional[timedelta] = Field(
        None,
        title=TITLE_LICENSE_TERM,
    )
    max_admins_count: Optional[int] = Field(
        None,
        gt=ZERO,
        title=TITLE_MAX_ADMINS_COUNT,
    )
    max_employees_count: Optional[int] = Field(
        None,
        gt=ZERO,
        title=TITLE_MAX_EMPLOYEES_COUNT,
    )

    @field_validator('name', mode='after')
    @classmethod
    def str_field(cls, value: str):
        return cls._validator_field_string(value)

    @field_validator('license_term', mode='before')
    @classmethod
    def interval_field(cls, value: int):
        return cls._validator_field_interval(value)

    model_config = ConfigDict(extra='forbid')


class LicenseTypeResponseSchema(BaseModel):
    """Схема лицензии для ответов."""

    id: int
    name: str
    license_term: timedelta
    max_admins_count: int
    max_employees_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LicenseTypeListResponseSchema(BaseModel):
    """Ответ с пагинацией для списка лицензий."""

    total: int = Field(..., description=TOTAL_DESCRIPTION)
    page: int = Field(..., description=PAGE_DESCRIPTION)
    page_size: int = Field(..., description=PAGE_SIZE_DESCRIPTION)
    items: List['LicenseTypeResponseSchema'] = Field(..., description=ITEMS_DESCRIPTION)


class LicenseTypeFilterSchema(BaseModel):
    """Схема фильтрации списка лицензий с возможностью сортировки."""

    name: Optional[str] = Field(None, description=FILTER_NAME_DESCRIPTION)

    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=SORTING_DESCRIPTION)

    page: Optional[int] = Field(DEFAULT_PAGE, ge=MIN_PAGE_SIZE, description=PAGE_DESCRIPTION)
    page_size: Optional[int] = Field(
        DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description=PAGE_SIZE_DESCRIPTION
    )
