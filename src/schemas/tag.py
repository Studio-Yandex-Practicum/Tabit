from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from src.core.constants.common import LENGTH_NAME_USER, MIN_LENGTH_NAME
from src.core.constants.user import title_company_id_tag, title_name_tag


class TagUserUpdateSchema(BaseModel):
    """Схема для частичного изменения тэгов пользователей."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_tag,
    )


class TagUserCreateSchema(TagUserUpdateSchema):
    """Схема для создания тэгов пользователей."""

    company_id: int = Field(
        ...,
        title=title_company_id_tag,
    )


class TagUserResponseSchema(BaseModel):
    """Схема тэгов пользователей для ответов."""

    id: int
    name: str
    company_id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(from_attributes=True)
