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
    """
    Параметры:
        name: Название.
        license_term: Срок действия лицензии в днях.
        max_admins_count: Максимально допустимое количество админов у компании.
        max_employees_count: Максимально допустимое количество сотрудников у компании.
    """

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

    model_config = ConfigDict(
        title='Схема создания лицензии',
        description='Схема для создания лицензии'
    )


class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """
    Параметры:
        name: Название.
        license_term: Срок действия лицензии в днях.
        max_admins_count: Максимально допустимое количество админов у компании.
        max_employees_count: Максимально допустимое количество сотрудников у компании.
    """

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

    model_config = ConfigDict(
        extra='forbid',
        title='Схема изменения лицензии',
        description='Схема для частичного изменения лицензии',
    )


class LicenseTypeResponseSchema(BaseModel):
    """
    Параметры:
        id: Идентификатор компании.
        name: Название.
        license_term: Срок действия лицензии в днях.
        max_admins_count: Максимально допустимое количество админов у компании.
        max_employees_count: Максимально допустимое количество сотрудников у компании.
        created_at: Дата создания записи в таблице.
        updated_at: Дата изменения записи в таблице.
    """

    id: int
    name: str
    license_term: timedelta
    max_admins_count: int
    max_employees_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True, title='Схема лицензии', description='Схема лицензии для ответов'
    )


class LicenseTypeListResponseSchema(BaseModel):
    """
    Параметры:
        items (List[LicenseTypeResponseSchema]): Список лицензий.
        total (int): Общее количество записей.
        page (int): Текущая страница.
        page_size (int): Количество записей на странице.
    """

    items: List[LicenseTypeResponseSchema]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(
        title='Схема списка лицензий', description='Схема ответа для списка лицензий с пагинацией'
    )


class LicenseTypeFilterSchema(BaseModel):
    """
    Параметры:
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

    model_config = ConfigDict(
        title='Схема фильтрации списка лицензий',
        description='Схема фильтрации списка лицензий с возможностью сортировки и пагинации',
    )
