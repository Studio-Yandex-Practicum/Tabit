from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Length, Title


class UserTagUpdateSchema(BaseModel):
    """Схема для частичного изменения тэгов пользователей."""

    name: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_TAG,
    )


class UserTagCreateSchema(UserTagUpdateSchema):
    """Схема для создания тэгов пользователей."""

    company_id: int = Field(
        ...,
        title=Title.COMPANY_ID_TAG,
    )


class UserTagResponseSchema(BaseModel):
    """Схема тэгов пользователей для ответов."""

    id: int
    name: str
    company_id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(from_attributes=True)
