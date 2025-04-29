from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.annotations import TagField
from src.schemas.constants import Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class TagBaseSchema(BaseModel):
    """
    Базовая схема для тегов пользователей.

    Определяет общие поля для схем тегов.

    Атрибуты:
        name (str): Название тега.
        company_id (Optional[int]): Идентификатор компании.
    """

    name: TagField = Field(..., title=Title.NAME_TAG)
    company_id: Optional[int] = Field(None, ge=1, title=Title.COMPANY_ID_TAG)

    model_config = BASE_CONFIG


class UserTagCreateSchema(TagBaseSchema):
    """
    Схема для создания тегов пользователей.

    Используется для добавления нового тега через API.

    Атрибуты:
        name (str): Название тега.
        company_id (int): Идентификатор компании.
    """

    company_id: int = Field(..., ge=1, title=Title.COMPANY_ID_TAG)

    model_config = BASE_CONFIG


class UserTagUpdateSchema(TagBaseSchema):
    """
    Схема для частичного изменения тегов пользователей.

    Используется для обновления названия тега через API.

    Атрибуты:
        name (str): Название тега.
        company_id (Optional[int]): Идентификатор компании.
    """

    name: TagField

    model_config = BASE_CONFIG


class UserTagResponseSchema(TagBaseSchema):
    """
    Схема тегов пользователей для ответов.

    Используется для возврата данных о теге через API.

    Атрибуты:
        id (int): Идентификатор тега.
        name (str): Название тега.
        company_id (int): Идентификатор компании.
        created_at (date): Дата создания тега.
        updated_at (date): Дата последнего обновления тега.
    """

    id: int
    name: TagField
    company_id: int
    created_at: date
    updated_at: date

    model_config = BASE_CONFIG
