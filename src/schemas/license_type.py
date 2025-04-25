from datetime import datetime, timedelta
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

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

# Типизация для повтор RENAMING полей
LicenseNameField = Annotated[
    str,
    StringConstraints(min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_LICENSE)
]
OptionalLicenseNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_LICENSE)
]
LicenseTermField = Annotated[
    timedelta,
    Field(ge=timedelta(**DEFAULT_LICENSE_TERM))
]
OptionalLicenseTermField = Annotated[
    Optional[timedelta],
    Field(ge=timedelta(**DEFAULT_LICENSE_TERM))
]
CountField = Annotated[int, Field(gt=ZERO)]
OptionalCountField = Annotated[Optional[int], Field(gt=ZERO)]
PageField = Annotated[Optional[int], Field(ge=MIN_PAGE_SIZE)]
PageSizeField = Annotated[
    Optional[int],
    Field(ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE)
]


class LicenseTypeBaseSchema(BaseModel):
    """Базовая схема лицензии.

    Определяет базовые поля и валидаторы для лицензии.
    """
    model_config = ConfigDict(extra='forbid')

    @field_validator('name', mode='after', check_fields=False)
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Проверяет отсутствие пробелов в начале или конце названия."""
        return validate_string(value)

    @field_validator('license_term', mode='before', check_fields=False)
    @classmethod
    def validate_license_term(cls, value: int) -> timedelta:
        """Проверяет и конвертирует срок действия лицензии в timedelta."""
        return validate_license_term(value)


class LicenseTypeCreateSchema(LicenseTypeBaseSchema):
    """Схема для создания лицензии.

    Поля:
        name: Название лицензии (обязательно).
        license_term: Срок действия лицензии (обязательно).
        max_admins_count: Максимальное количество администраторов (обязательно).
        max_employees_count: Максимальное количество сотрудников (обязательно).
    """
    name: LicenseNameField = Field(..., title=TITLE_NAME_LICENSE)
    license_term: LicenseTermField = Field(..., title=TITLE_LICENSE_TERM)
    max_admins_count: CountField = Field(..., title=TITLE_MAX_MODERATORS_COUNT)
    max_employees_count: CountField = Field(..., title=TITLE_MAX_EMPLOYEES_COUNT)


class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """Схема для частичного обновления лицензии.

    Поля:
        name: Название лицензии (опционально).
        license_term: Срок действия лицензии (опционально).
        max_admins_count: Максимальное количество администраторов (опционально).
        max_employees_count: Максимальное количество сотрудников (опционально).
    """
    name: OptionalLicenseNameField = Field(None, title=TITLE_NAME_LICENSE)
    license_term: OptionalLicenseTermField = Field(None, title=TITLE_LICENSE_TERM)
    max_admins_count: OptionalCountField = Field(None, title=TITLE_MAX_MODERATORS_COUNT)
    max_employees_count: OptionalCountField = Field(None, title=TITLE_MAX_EMPLOYEES_COUNT)

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

    model_config = ConfigDict(from_attributes=True)


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
    page: PageField = Field(DEFAULT_PAGE, description=PAGE_DESCRIPTION)
    page_size: PageSizeField = Field(DEFAULT_PAGE_SIZE, description=PAGE_SIZE_DESCRIPTION)

    model_config = ConfigDict(extra='forbid')