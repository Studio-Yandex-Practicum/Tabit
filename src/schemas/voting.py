from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)

VotingText = Annotated[str, StringConstraints(min_length=1, max_length=1000)]

class VotingBase(BaseModel):
    """Базовая схема для голосования."""
    text: VotingText = Field(..., title="Текст голосования")
    message_id: int = Field(..., ge=1, title="ID сообщения")

    model_config = BASE_CONFIG

class VotingCreate(VotingBase):
    """Схема для создания голосования."""
    model_config = BASE_CONFIG

class VotingInDB(VotingBase):
    """Схема голосования в базе данных."""
    id: int = Field(..., title="ID голосования")

    model_config = BASE_CONFIG

class VotingByUserBase(BaseModel):
    """Базовая схема для голосования пользователя."""
    user_id: UUID = Field(..., title="ID пользователя")
    voting_id: int = Field(..., ge=1, title="ID голосования")

    model_config = BASE_CONFIG

class VotingByUserCreate(VotingByUserBase):
    """Схема для голосования пользователя."""
    model_config = BASE_CONFIG

class VotingByUserInDB(VotingByUserBase):
    """Схема голосования пользователя в базе данных."""
    id: int = Field(..., title="ID записи")

    model_config = BASE_CONFIG