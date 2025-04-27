from datetime import datetime, timedelta
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from src.schemas.constants import Default, Length, MiscConstants, Title
from src.schemas.validators.license_type import (
    validate_license_term,
    validate_string,
)

# Типизация для повторяющихся полей
LicenseNameField = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
OptionalLicenseNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
LicenseTermField = Annotated[
    timedelta,
    Field(ge=timedelta(**Default.LICENSE_TERM))
]
OptionalLicenseTermField = Annotated[
    Optional[timedelta],
    Field(ge=timedelta(**Default.LICENSE_TERM))
]
CountField = Annotated[int, Field(gt=MiscConstants.ZERO)]
OptionalCountField = Annotated[Optional[int], Field(gt=MiscConstants.ZERO)]
PageField = Annotated[Optional[int], Field(ge=Default.MIN_PAGE_SIZE)]
PageSizeField = Annotated[
    Optional[int],
    Field(ge=Default.MIN_PAGE_SIZE, le=Default.MAX_PAGE_SIZE)
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
    name: LicenseNameField = Field(..., title=Title.NAME_LICENSE)
    license_term: LicenseTermField = Field(..., title=Title.TERM_LICENSE)
    max_admins_count: CountField = Field(..., title=Title.MAX_MODERATORS_COUNT)
    max_employees_count: CountField = Field(..., title=Title.MAX_EMPLOYEES_COUNT)

class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """Схема для частичного обновления лицензии.

    Поля:
        name: Название лицензии (опционально).
        license_term: Срок действия лицензии (опционально).
        max_admins_count: Максимальное количество администраторов (опционально).
        max_employees_count: Максимальное количество сотрудников (опционально).
    """
    name: OptionalLicenseNameField = Field(None, title=Title.NAME_LICENSE)
    license_term: OptionalLicenseTermField = Field(None, title=Title.TERM_LICENSE)
    max_admins_count: OptionalCountField = Field(None, title=Title.MAX_MODERATORS_COUNT)
    max_employees_count: OptionalCountField = Field(None, title=Title.MAX_EMPLOYEES_COUNT)

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
    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)
    page: PageField = Field(Default.PAGE, description=Default.PAGE_DESCRIPTION)
    page_size: PageSizeField = Field(Default.PAGE_SIZE, description=Default.PAGE_SIZE_DESCRIPTION)

    model_config = ConfigDict(extra='forbid')