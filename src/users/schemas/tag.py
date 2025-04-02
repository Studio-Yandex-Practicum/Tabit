from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.constants import LENGTH_NAME_USER, MIN_LENGTH_NAME
from src.users.constants import title_name_tag
from src.users.tag_validators import validate_name, validate_uuid_user


class TagUserUpdateSchema(BaseModel):
    """Схема для частичного изменения тэгов пользователей."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_tag,
    )

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        """Валидирует название тэга."""
        return validate_name(value)


class TagUserCreateSchema(TagUserUpdateSchema):
    """Схема для создания тэгов пользователей."""

    user_id: UUID = Field(..., title='Идентификатор пользователя')

    @field_validator('user_id')
    @classmethod
    def validate_uuid_user(cls, value: Optional[UUID]) -> Optional[UUID]:
        """Валидирует uuid пользователя."""
        if value is not None:
            return validate_uuid_user(value)
        return value


class TagUserResponseSchema(BaseModel):
    """Схема тэгов пользователей для ответов."""

    id: int
    name: str
    company_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
