from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from src.schemas.constants import (
    LENGTH_NAME_USER,
    MIN_LENGTH_NAME,
    TITLE_COMPANY_ID_TAG,
    TITLE_NAME_TAG,
)

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

TagNameStr = Annotated[
    str, StringConstraints(min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_USER)
]

class TagBaseSchema(BaseModel):
    """Базовая схема для тегов пользователей."""
    name: TagNameStr = Field(..., title=TITLE_NAME_TAG)
    company_id: Optional[int] = Field(None, ge=1, title=TITLE_COMPANY_ID_TAG)

    model_config = BASE_CONFIG

class UserTagCreateSchema(TagBaseSchema):
    """Схема для создания тегов пользователей."""
    company_id: int = Field(..., ge=1, title=TITLE_COMPANY_ID_TAG)

    model_config = BASE_CONFIG

class UserTagUpdateSchema(TagBaseSchema):
    """Схема для частичного изменения тегов пользователей."""
    name: TagNameStr

    model_config = BASE_CONFIG

class UserTagResponseSchema(TagBaseSchema):
    """Схема тегов пользователей для ответов."""
    id: int
    name: TagNameStr
    company_id: int
    created_at: date
    updated_at: date

    model_config = BASE_CONFIG