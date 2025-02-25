from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.problems.constants import TITLE_COMMENTS_TEXT_CREATE, TITLE_COMMENTS_TEXT_UPDATE


class CommentBase(BaseModel):
    """Базовая схема для комментариев."""

    text: str
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class CommentCreate(CommentBase):
    """Схема для создания комментария к треду."""

    text: str = Field(..., title=TITLE_COMMENTS_TEXT_CREATE)


class CommentUpdate(CommentBase):
    """Схема для обновления комментария."""

    text: str = Field(..., title=TITLE_COMMENTS_TEXT_UPDATE)


class CommentRead(CommentBase):
    """Схема комментария для ответов API."""

    id: int
    message_id: int
    owner_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)