from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.problems.constants import TITLE_COMMENTS_TEXT_CREATE, TITLE_COMMENTS_TEXT_UPDATE


class CommentBase(BaseModel):
    """Базовая схема для комментариев."""

    text: str
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class CommentCreate(CommentBase):
    """
    Параметры:
        text: текст создаваемого комментария.
    """

    text: str = Field(..., title=TITLE_COMMENTS_TEXT_CREATE)

    model_config = ConfigDict(
        title='Схема создания коммента',
        description='Схема для создания нового комментария'
    )


class CommentUpdate(CommentBase):
    """
    Параметры:
        text: обновленный текст комментария.
    """

    text: str = Field(..., title=TITLE_COMMENTS_TEXT_UPDATE)

    model_config = ConfigDict(
        title='Схема обновления коммента',
        description='Схема для обновления комментария'
    )


class CommentRead(CommentBase):
    """
    Параметры:
        id: идентификатор.
        message_id: идентификатор треда, к которому относится комментарий.
        owner_id: автор комментария.
        rating: рейтинг комментария.
        created_at: дата создания комментария.
        updated_at: дата изменения комментария.
    """

    id: int
    message_id: int
    owner_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        title='Схема комментария',
        description='Схема комментария для ответов API',
    )
