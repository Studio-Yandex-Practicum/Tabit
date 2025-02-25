from datetime import datetime, timedelta
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.constants import LENGTH_NAME_LICENSE, MIN_LENGTH_NAME, ZERO
from src.tabit_management.constants import (
    DEFAULT_LICENSE_TERM,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    FILTER_NAME_DESCRIPTION,
    MAX_PAGE_SIZE,
    MIN_PAGE_SIZE,
    PAGE_DESCRIPTION,
    PAGE_SIZE_DESCRIPTION,
    SORTING_DESCRIPTION,
    TITLE_LICENSE_TERM,
    TITLE_MAX_ADMINS_COUNT,
    TITLE_MAX_EMPLOYEES_COUNT,
    TITLE_NAME_LICENSE,
)
from src.tabit_management.validators.license_type_validators import (
    validate_license_term,
    validate_string,
)


class LicenseTypeBaseSchema(BaseModel):
    """Базовая схема лицензии, содержащая валидаторы."""

    @field_validator('name', mode='after', check_fields=False)
    @classmethod
    def validate_name(cls, value: str):
        return validate_string(value)

    @field_validator('license_term', mode='before', check_fields=False)
    @classmethod
    def validate_license_term(cls, value: int):
        return validate_license_term(value)


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
    """
    Схема ответа для списка лицензий с пагинацией.

    Attributes:
        items (List[LicenseTypeResponseSchema]): Список лицензий.
        total (int): Общее количество записей.
        page (int): Текущая страница.
        page_size (int): Количество записей на странице.
    """

    items: List[LicenseTypeResponseSchema]
    total: int
    page: int
    page_size: int


class LicenseTypeFilterSchema(BaseModel):
    """
    Схема фильтрации списка лицензий с возможностью сортировки и пагинации.

    Attributes:
        name (Optional[str]): Фильтр по названию лицензии.
        ordering (Optional[Literal]): Сортировка (по полям name, created_at, updated_at).
        page (Optional[int]): Номер страницы.
        page_size (Optional[int]): Количество записей на странице.
    """

    name: Optional[str] = Field(None, description=FILTER_NAME_DESCRIPTION)

    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=SORTING_DESCRIPTION)

    page: Optional[int] = Field(DEFAULT_PAGE, ge=MIN_PAGE_SIZE, description=PAGE_DESCRIPTION)
    page_size: Optional[int] = Field(
        DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description=PAGE_SIZE_DESCRIPTION
    )
