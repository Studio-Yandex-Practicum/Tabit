from datetime import datetime, timedelta
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.constants import DefaultConstants, LengthConstants, MiscConstants, TitleConstants
from src.schemas.validators.license_type import (
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
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME_LICENSE,
        title=TitleConstants.NAME_LICENSE,
    )
    license_term: timedelta = Field(
        ...,
        ge=timedelta(**DefaultConstants.LICENSE_TERM),
        title=TitleConstants.TERM_LICENSE,
    )
    max_admins_count: int = Field(
        ...,
        gt=MiscConstants.ZERO,
        title=TitleConstants.MAX_MODERATORS_COUNT,
    )
    max_employees_count: int = Field(
        ...,
        gt=MiscConstants.ZERO,
        title=TitleConstants.MAX_EMPLOYEES_COUNT,
    )


class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """Схема для частичного изменения лицензии."""

    name: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME_LICENSE,
        title=TitleConstants.NAME_LICENSE,
    )
    license_term: Optional[timedelta] = Field(
        None,
        title=TitleConstants.TERM_LICENSE,
    )
    max_admins_count: Optional[int] = Field(
        None,
        gt=MiscConstants.ZERO,
        title=TitleConstants.MAX_MODERATORS_COUNT,
    )
    max_employees_count: Optional[int] = Field(
        None,
        gt=MiscConstants.ZERO,
        title=TitleConstants.MAX_EMPLOYEES_COUNT,
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

    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)

    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)

    page: Optional[int] = Field(
        DefaultConstants.PAGE,
        ge=DefaultConstants.MIN_PAGE_SIZE,
        description=DefaultConstants.PAGE_DESCRIPTION,
    )
    page_size: Optional[int] = Field(
        DefaultConstants.PAGE_SIZE,
        ge=DefaultConstants.MIN_PAGE_SIZE,
        le=DefaultConstants.MAX_PAGE_SIZE,
        description=DefaultConstants.PAGE_SIZE_DESCRIPTION,
    )
