from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import (
    DEFAULT_LIMIT,
    DEFAULT_SKIP,
    FILTER_NAME_DESCRIPTION,
    MAX_PAGE_SIZE,
    SORTING_DESCRIPTION,
)

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

class BaseFilterSchema(BaseModel):
    """
    Базовая схема для обработки query-параметров: пагинация, сортировка, фильтрация.
    """
    skip: int = Field(DEFAULT_SKIP, ge=0, title="Пропустить n объектов")
    limit: int = Field(
        DEFAULT_LIMIT, ge=1, le=MAX_PAGE_SIZE, title="Лимитировать список объектов"
    )
    name: Optional[str] = Field(None, description=FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal["name", "-name", "created_at", "-created_at", "updated_at", "-updated_at"]
    ] = Field(None, description=SORTING_DESCRIPTION)

    model_config = BASE_CONFIG

class CompanyFilterSchema(BaseFilterSchema):
    """
    Схема фильтрации списка компаний под query-параметры.

    TODO: Добавить специфические поля фильтрации (например, is_active, license_id).
    """
    model_config = BASE_CONFIG

class UserFilterSchema(BaseFilterSchema):
    """
    Схема фильтрации списка пользователей под query-параметры.

    TODO: Добавить специфические поля фильтрации (например, role, department_id).
    """
    model_config = BASE_CONFIG