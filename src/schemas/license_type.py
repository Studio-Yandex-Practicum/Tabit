from datetime import datetime, timedelta
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.constants import (
    DEFAULT_LICENSE_TERM,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    FILTER_NAME_DESCRIPTION,
    LENGTH_NAME_LICENSE,
    MAX_PAGE_SIZE,
    MIN_LENGTH_NAME,
    MIN_PAGE_SIZE,
    PAGE_DESCRIPTION,
    PAGE_SIZE_DESCRIPTION,
    SORTING_DESCRIPTION,
    TITLE_LICENSE_TERM,
    TITLE_MAX_EMPLOYEES_COUNT,
    TITLE_MAX_MODERATORS_COUNT,
    TITLE_NAME_LICENSE,
    ZERO,
)
from src.schemas.validators.license_type import (
    validate_license_term,
    validate_string,
)


class LicenseTypeBaseSchema(BaseModel):
    """Базовая схема лицензии.

    Определяет базовые поля и валидаторы для лицензии.
    """
    model_config = ConfigDict(extra='forbid')

    @field_validator('name', mode='after', check_fields=False)
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Проверяет, что название лицензии не содержит пробелов в начале или конце."""
        return validate_string(value)

    @field_validator('license_term', mode='before', check_fields=False)
    @classmethod
    def validate_license_term(cls, value: int) -> timedelta:
        """Проверяет и конвертирует срок действия лицензии в timedelta."""
        return validate_license_term(value)


class LicenseTypeCreateSchema(LicenseTypeBaseSchema):
    """Схема для создания лицензии.

    Поля:
        name: Название лицензии (от 1 до 255 символов, без пробелов в начале/конце).
        license_term: Срок действия лицензии (не менее 1 дня).
        max_admins_count: Максимальное количество администраторов (> 0).
        max_employees_count: Максимальное количество сотрудников (> 0).
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
        title=TITLE_MAX_MODERATORS_COUNT,
    )
    max_employees_count: int = Field(
        ...,
        gt=ZERO,
        title=TITLE_MAX_EMPLOYEES_COUNT,
    )


class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """Схема для частичного обновления лицензии.

    Поля:
        name: Название лицензии (опционально, от 1 до 255 символов, без пробелов).
        license_term: Срок действия лицензии (опционально, не менее 1 дня).
        max_admins_count: Максимальное количество администраторов (опционально, > 0).
        max_employees_count: Максимальное количество сотрудников (опционально, > 0).
    """
    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_LICENSE,
        title=TITLE_NAME_LICENSE,
    )
    license_term: Optional[timedelta] = Field(
        None,
        ge=timedelta(**DEFAULT_LICENSE_TERM),
        title=TITLE_LICENSE_TERM,
    )
    max_admins_count: Optional[int] = Field(
        None,
        gt=ZERO,
        title=TITLE_MAX_MODERATORS_COUNT,
    )
    max_employees_count: Optional[int] = Field(
        None,
        gt=ZERO,
        title=TITLE_MAX_EMPLOYEES_COUNT,
    )

    model_config = ConfigDict(extra='forbid')


class LicenseTypeResponseSchema(BaseModel):
    """Схема лицензии для ответа.

    Поля:
        id: Идентификатор лицензии.
        name: Название лицензии.
        license_term: Срок действия лицензии.
        max_admins_count: Максимальное количество администраторов.
        max_employees_count: Максимальное количество сотрудников.
        created_at: Время создания.
        updated_at: Время обновления.
    """
    id: int
    name: str
    license_term: timedelta
    max_admins_count: int
    max_employees_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LicenseTypeListResponseSchema(BaseModel):
    """Схема ответа для списка лицензий с пагинацией.

    Поля:
        items: Список лицензий.
        total: Общее количество записей.
        page: Текущая страница.
        page_size: Количество записей на странице.
    """
    items: List[LicenseTypeResponseSchema]
    total: int
    page: int
    page_size: int


class LicenseTypeFilterSchema(BaseModel):
    """Схема фильтрации списка лицензий.

    Поля:
        name: Фильтр по названию лицензии (опционально).
        ordering: Сортировка по полям (опционально).
        page: Номер страницы (по умолчанию 1).
        page_size: Количество записей на странице (по умолчанию 10).
    """
    name: Optional[str] = Field(None, description=FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=SORTING_DESCRIPTION)
    page: Optional[int] = Field(
        DEFAULT_PAGE,
        ge=MIN_PAGE_SIZE,
        description=PAGE_DESCRIPTION,
    )
    page_size: Optional[int] = Field(
        DEFAULT_PAGE_SIZE,
        ge=MIN_PAGE_SIZE,
        le=MAX_PAGE_SIZE,
        description=PAGE_SIZE_DESCRIPTION,
    )

    model_config = ConfigDict(extra='forbid')