from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from src.schemas.constants import Length, Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)

CommentText = Annotated[
    str, StringConstraints(min_length=1, max_length=Length.MAX_COMMENT_TEXT_LENGTH)
]


class CommentBase(BaseModel):
    """Базовая схема для комментариев."""

    text: CommentText = Field(..., title=Title.CREATE_COMMENTS_TEXT)

    model_config = BASE_CONFIG


class CommentCreate(CommentBase):
    """Схема для создания комментария к треду."""

    model_config = BASE_CONFIG


class CommentUpdate(CommentBase):
    """Схема для обновления комментария."""

    text: CommentText = Field(..., title=Title.UPDATE_COMMENTS_TEXT)

    model_config = BASE_CONFIG


class CommentRead(CommentBase):
    """Схема комментария для ответов API."""

    id: int
    message_id: int
    owner_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime

    model_config = BASE_CONFIG
