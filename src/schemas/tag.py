from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import LengthConstants, TitleConstants


class UserTagUpdateSchema(BaseModel):
    """Схема для частичного изменения тэгов пользователей."""

    name: str = Field(
        ...,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.NAME_TAG,
    )


class UserTagCreateSchema(UserTagUpdateSchema):
    """Схема для создания тэгов пользователей."""

    company_id: int = Field(
        ...,
        title=TitleConstants.COMPANY_ID_TAG,
    )


class UserTagResponseSchema(BaseModel):
    """Схема тэгов пользователей для ответов."""

    id: int
    name: str
    company_id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(from_attributes=True)
