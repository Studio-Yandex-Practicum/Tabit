from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Default, MiscConstants, Title

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

class BaseFilterSchema(BaseModel):
    """
    Базовая схема для обработки query-параметров: пагинация, сортировка, фильтрация.
    """
    skip: int = Field(Default.SKIP, ge=0, title=Title.SKIP)
    limit: int = Field(
        Default.LIMIT, ge=1, le=Default.MAX_PAGE_SIZE, title=Title.LIMIT
    )
    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal["name", "-name", "created_at", "-created_at", "updated_at", "-updated_at"]
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)

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