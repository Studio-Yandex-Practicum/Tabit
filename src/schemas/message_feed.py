from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.annotations import TextField
from src.schemas.constants import Title

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class MessageFeedBase(BaseModel):
    """
    Базовая схема для тредов.

    Определяет общие поля для схем тредов.

    Атрибуты:
        text (str): Текст треда.
        important (bool): Флаг важности треда (по умолчанию False).
    """

    text: TextField = Field(..., title=Title.MESSAGE_FEED_TEXT)
    important: bool = Field(False, title=Title.MESSAGE_FEED_IMPORTANT)

    model_config = BASE_CONFIG


class MessageFeedCreate(MessageFeedBase):
    """
    Схема для создания нового треда к проблеме.

    Используется для добавления нового треда через API.

    Атрибуты:
        text (str): Текст треда.
        important (bool): Флаг важности треда (по умолчанию False).
    """

    model_config = BASE_CONFIG


class MessageFeedRead(MessageFeedBase):
    """
    Схема треда для ответов API.

    Используется для возврата данных о треде через API.

    Атрибуты:
        id (int): Идентификатор треда.
        problem_id (int): Идентификатор связанной проблемы.
        owner_id (UUID): Идентификатор владельца треда.
        created_at (datetime): Время создания треда.
        updated_at (datetime): Время последнего обновления треда.
        text (str): Текст треда.
        important (bool): Флаг важности треда.
    """

    id: int
    problem_id: int
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = BASE_CONFIG
