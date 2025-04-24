from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

from src.schemas.constants import TITLE_MESSAGE_FEED_IMPORTANT, TITLE_MESSAGE_FEED_TEXT

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

MessageText = Annotated[str, StringConstraints(min_length=1, max_length=1000)]

class MessageFeedBase(BaseModel):
    """Базовая схема для тредов."""
    text: MessageText = Field(..., title=TITLE_MESSAGE_FEED_TEXT)
    important: bool = Field(False, title=TITLE_MESSAGE_FEED_IMPORTANT)

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