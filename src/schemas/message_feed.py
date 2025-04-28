from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Title
from src.schemas.types import TextField

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)



class MessageFeedBase(BaseModel):
    """Базовая схема для тредов."""

    text: TextField = Field(..., title=Title.MESSAGE_FEED_TEXT)
    important: bool = Field(False, title=Title.MESSAGE_FEED_IMPORTANT)

    model_config = BASE_CONFIG


class MessageFeedCreate(MessageFeedBase):
    """Схема для создания нового треда к проблеме."""

    model_config = BASE_CONFIG


class MessageFeedRead(MessageFeedBase):
    """Схема треда для ответов API."""

    id: int
    problem_id: int
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = BASE_CONFIG
