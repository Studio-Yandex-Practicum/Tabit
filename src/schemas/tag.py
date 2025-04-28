from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Title
from src.schemas.types import TagField

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)



class TagBaseSchema(BaseModel):
    """Базовая схема для тегов пользователей."""
    name: TagField = Field(..., title=Title.NAME_TAG)
    company_id: Optional[int] = Field(None, ge=1, title=Title.COMPANY_ID_TAG)

    model_config = BASE_CONFIG

class UserTagCreateSchema(TagBaseSchema):
    """Схема для создания тегов пользователей."""
    company_id: int = Field(..., ge=1, title=Title.COMPANY_ID_TAG)

    model_config = BASE_CONFIG

class UserTagUpdateSchema(TagBaseSchema):
    """Схема для частичного изменения тегов пользователей."""
    name: TagField

    model_config = BASE_CONFIG

class UserTagResponseSchema(TagBaseSchema):
    """Схема тегов пользователей для ответов."""
    id: int
    name: TagField
    company_id: int
    created_at: date
    updated_at: date

    model_config = BASE_CONFIG