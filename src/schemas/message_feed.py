from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Title


class MessageFeedBase(BaseModel):
    """Базовая схема для тредов."""

    text: str
    important: bool
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class MessageFeedCreate(MessageFeedBase):
    """Схема для создания нового треда к проблеме."""

    text: str = Field(..., title=Title.MESSAGE_FEED_TEXT)
    important: bool = Field(False, title=Title.MESSAGE_FEED_IMPORTANT)


class MessageFeedRead(MessageFeedBase):
    """Схема треда для ответов API."""

    id: int
    problem_id: int
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
