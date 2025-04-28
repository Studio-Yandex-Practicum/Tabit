from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import Title
from src.schemas.types import VotingTextField

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    from_attributes=True,
)


class VotingBase(BaseModel):
    """Базовая схема для голосования."""
    text: VotingTextField = Field(..., title=Title.VOTING_TEXT)
    message_id: int = Field(..., ge=1, title=Title.VOTING_MESSAGE_ID)

    model_config = BASE_CONFIG

class VotingCreate(VotingBase):
    """Схема для создания голосования."""
    model_config = BASE_CONFIG

class VotingInDB(VotingBase):
    """Схема голосования в базе данных."""
    id: int = Field(..., title=Title.VOTING_ID)

    model_config = BASE_CONFIG

class VotingByUserBase(BaseModel):
    """Базовая схема для голосования пользователя."""
    user_id: UUID = Field(..., title=Title.VOTING_USER_ID)
    voting_id: int = Field(..., ge=1, title=Title.VOTING_ID)

    model_config = BASE_CONFIG

class VotingByUserCreate(VotingByUserBase):
    """Схема для голосования пользователя."""
    model_config = BASE_CONFIG

class VotingByUserInDB(VotingByUserBase):
    """Схема голосования пользователя в базе данных."""
    id: int = Field(..., title=Title.VOTING_RECORD_ID)

    model_config = BASE_CONFIG