from datetime import datetime, timedelta
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.annotations import (
    CountField,
    LicenseNameField,
    LicenseTermField,
    OptionalCountField,
    OptionalLicenseNameField,
    OptionalLicenseTermField,
    PageField,
    PageSizeField,
)
from src.schemas.constants import DefaultConstants, MiscConstants, TitleConstants
from src.schemas.validators.license_type import (
    validate_license_term,
    validate_string,
)


class LicenseTypeBaseSchema(BaseModel):
    """
    Базовая схема лицензии.

    Определяет общие поля и валидаторы для схем лицензий.

    Атрибуты:
        name (str): Название лицензии.
        license_term (timedelta): Срок действия лицензии.

    Валидаторы:
        validate_name: Проверяет отсутствие пробелов в начале или конце названия.
        validate_license_term: Проверяет и конвертирует срок действия лицензии в timedelta.
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
    """
    Схема для создания лицензии.

    Используется для добавления новой лицензии через API.

    Атрибуты:
        name (str): Название лицензии.
        license_term (timedelta): Срок действия лицензии.
        max_admins_count (int): Максимальное количество администраторов.
        max_employees_count (int): Максимальное количество сотрудников.

    Валидаторы:
        validate_name: Проверяет отсутствие пробелов в начале или конце названия.
        validate_license_term: Проверяет и конвертирует срок действия лицензии в timedelta.
    """

    name: LicenseNameField = Field(..., title=TitleConstants.NAME_LICENSE)
    license_term: LicenseTermField = Field(..., title=TitleConstants.TERM_LICENSE)
    max_admins_count: CountField = Field(..., title=TitleConstants.MAX_MODERATORS_COUNT)
    max_employees_count: CountField = Field(..., title=TitleConstants.MAX_EMPLOYEES_COUNT)


class LicenseTypeUpdateSchema(LicenseTypeBaseSchema):
    """
    Схема для частичного обновления лицензии.

    Используется для изменения данных лицензии через API.

    Атрибуты:
        name (Optional[str]): Название лицензии.
        license_term (Optional[timedelta]): Срок действия лицензии.
        max_admins_count (Optional[int]): Максимальное количество администраторов.
        max_employees_count (Optional[int]): Максимальное количество сотрудников.

    Валидаторы:
        validate_name: Проверяет отсутствие пробелов в начале или конце названия.
        validate_license_term: Проверяет и конвертирует срок действия лицензии в timedelta.
    """

    name: OptionalLicenseNameField = Field(None, title=TitleConstants.NAME_LICENSE)
    license_term: OptionalLicenseTermField = Field(None, title=TitleConstants.TERM_LICENSE)
    max_admins_count: OptionalCountField = Field(None, title=TitleConstants.MAX_MODERATORS_COUNT)
    max_employees_count: OptionalCountField = Field(None, title=TitleConstants.MAX_EMPLOYEES_COUNT)

    model_config = ConfigDict(extra='forbid')


class LicenseTypeResponseSchema(BaseModel):
    """
    Схема лицензии для ответа.

    Используется для возврата данных о лицензии через API.

    Атрибуты:
        id (int): Идентификатор лицензии.
        name (str): Название лицензии.
        license_term (timedelta): Срок действия лицензии.
        max_admins_count (int): Максимальное количество администраторов.
        max_employees_count (int): Максимальное количество сотрудников.
        created_at (datetime): Время создания лицензии.
        updated_at (datetime): Время последнего обновления лицензии.
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
    """
    Схема ответа для списка лицензий с пагинацией.

    Используется для возврата списка лицензий с информацией о пагинации через API.

    Атрибуты:
        items (List[LicenseTypeResponseSchema]): Список лицензий.
        total (int): Общее количество записей.
        page (int): Текущая страница.
        page_size (int): Количество записей на странице.
    """

    items: List[LicenseTypeResponseSchema]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


class LicenseTypeFilterSchema(BaseModel):
    """
    Схема фильтрации списка лицензий.

    Используется для фильтрации и сортировки списка лицензий через API.

    Атрибуты:
        name (Optional[str]): Фильтр по названию лицензии.
        ordering (Optional[str]): Сортировка по полям
            (name, created_at, updated_at, с префиксом '-' для обратной сортировки).
        page (int): Номер страницы (по умолчанию 1).
        page_size (int): Количество записей на странице (по умолчанию 10).
    """

    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)
    page: PageField = Field(DefaultConstants.PAGE, description=DefaultConstants.PAGE_DESCRIPTION)
    page_size: PageSizeField = Field(
        DefaultConstants.PAGE_SIZE, description=DefaultConstants.PAGE_SIZE_DESCRIPTION
    )

    model_config = ConfigDict(extra='forbid')
