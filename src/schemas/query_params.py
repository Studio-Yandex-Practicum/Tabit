from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Default, MiscConstants, Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class BaseFilterSchema(BaseModel):
    """
    Базовая схема для обработки query-параметров: пагинация, сортировка, фильтрация.

    Используется для задания параметров фильтрации, сортировки и пагинации в API-запросах.

    Атрибуты:
        skip (int): Количество записей для пропуска (по умолчанию 0).
        limit (int): Максимальное количество записей на странице (по умолчанию 10, максимум 100).
        name (Optional[str]): Фильтр по имени.
        ordering (Optional[str]): Сортировка по полям
            (name, created_at, updated_at, с префиксом '-' для обратной сортировки).
    """

    skip: int = Field(Default.SKIP, ge=0, title=Title.SKIP)
    limit: int = Field(Default.LIMIT, ge=1, le=Default.MAX_PAGE_SIZE, title=Title.LIMIT)
    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)

    model_config = BASE_CONFIG


class CompanyFilterSchema(BaseFilterSchema):
    """
    Схема фильтрации списка компаний под query-параметры.

    Используется для фильтрации, сортировки и пагинации списка компаний в API.

    Атрибуты:
        skip (int): Количество записей для пропуска (по умолчанию 0).
        limit (int): Максимальное количество записей на странице (по умолчанию 10, максимум 100).
        name (Optional[str]): Фильтр по имени компании.
        ordering (Optional[str]): Сортировка по полям
            (name, created_at, updated_at, с префиксом '-' для обратной сортировки).
    """

    # TODO: Добавить специфические поля фильтрации (например, is_active, license_id).

    model_config = BASE_CONFIG


class UserFilterSchema(BaseFilterSchema):
    """
    Схема фильтрации списка пользователей под query-параметры.

    Используется для фильтрации, сортировки и пагинации списка пользователей в API.

    Атрибуты:
        skip (int): Количество записей для пропуска (по умолчанию 0).
        limit (int): Максимальное количество записей на странице (по умолчанию 10, максимум 100).
        name (Optional[str]): Фильтр по имени пользователя.
        ordering (Optional[str]): Сортировка по полям
            (name, created_at, updated_at, с префиксом '-' для обратной сортировки).
    """

    # TODO: Добавить специфические поля фильтрации (например, role, department_id).

    model_config = BASE_CONFIG
