from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.annotations import CommentTextField
from src.schemas.constants import TitleConstants

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class CommentBase(BaseModel):
    """
    Базовая схема для комментариев.

    Определяет общие поля для схем комментариев.

    Атрибуты:
        text (str): Текст комментария.
    """

    text: CommentTextField = Field(..., title=TitleConstants.CREATE_COMMENTS_TEXT)

    model_config = BASE_CONFIG


class CommentCreate(CommentBase):
    """
    Схема для создания комментария к треду.

    Используется для добавления нового комментария через API.

    Атрибуты:
        text (str): Текст комментария.
    """

    model_config = BASE_CONFIG


class CommentUpdate(CommentBase):
    """
    Схема для обновления комментария.

    Используется для изменения текста существующего комментария через API.

    Атрибуты:
        text (str): Текст комментария.
    """

    text: CommentTextField = Field(..., title=TitleConstants.UPDATE_COMMENTS_TEXT)

    model_config = BASE_CONFIG


class CommentRead(CommentBase):
    """
    Схема комментария для ответов API.

    Используется для возврата данных о комментарии в API.

    Атрибуты:
        id (int): Идентификатор комментария.
        message_id (int): Идентификатор сообщения, к которому относится комментарий.
        owner_id (UUID): Идентификатор владельца комментария.
        rating (int): Рейтинг комментария.
        created_at (datetime): Время создания комментария.
        updated_at (datetime): Время последнего обновления комментария.
        text (str): Текст комментария.
    """

    id: int
    message_id: int
    owner_id: UUID
    rating: int
    created_at: datetime
    updated_at: datetime

    model_config = BASE_CONFIG
