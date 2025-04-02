from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.problems.constants import TITLE_MESSAGE_FEED_IMPORTANT, TITLE_MESSAGE_FEED_TEXT


class MessageFeedBase(BaseModel):
    """
    Параметры:
        text: Название треда.
        important: Есть возможность указать, что сообщение важное.
    """

    text: str
    important: bool

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
        title='Схема тредов',
        description='Базовая схема для тредов',
    )


class MessageFeedCreate(MessageFeedBase):
    """
    Параметры:
        text: Название треда.
        important: Есть возможность указать, что сообщение важное.
    """

    text: str = Field(..., title=TITLE_MESSAGE_FEED_TEXT)
    important: bool = Field(False, title=TITLE_MESSAGE_FEED_IMPORTANT)

    model_config = ConfigDict(
        title='Схема создания тредов', description='Схема для создания нового треда к проблеме'
    )


class MessageFeedRead(MessageFeedBase):
    """
    Параметры:
        id: Идентификатор.
        problem_id: Идентификатор проблемы, к которой относится лента сообщений.
        owner_id: Автор сообщения.
        created_at: Дата создания.
        updated_at: Дата изменения.
    """

    id: int
    problem_id: int
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True, title='Схема треда', description='Схема треда для ответов API'
    )
