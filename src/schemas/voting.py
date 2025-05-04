from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.annotations import VotingTextField
from src.schemas.constants import TitleConstants

BASE_CONFIG = ConfigDict(
    extra='forbid',
    str_strip_whitespace=True,
    from_attributes=True,
)


class VotingBase(BaseModel):
    """
    Базовая схема для голосования.

    Определяет общие поля для схем голосования.

    Атрибуты:
        text (str): Текст голосования.
        message_id (int): Идентификатор связанного сообщения.
    """

    text: VotingTextField = Field(..., title=TitleConstants.VOTING_TEXT)
    message_id: int = Field(..., ge=1, title=TitleConstants.VOTING_MESSAGE_ID)

    model_config = BASE_CONFIG


class VotingCreate(VotingBase):
    """
    Схема для создания голосования.

    Используется для добавления нового голосования через API.

    Атрибуты:
        text (str): Текст голосования.
        message_id (int): Идентификатор связанного сообщения.
    """

    model_config = BASE_CONFIG


class VotingInDB(VotingBase):
    """
    Схема голосования в базе данных.

    Используется для представления данных о голосовании, хранящихся в базе данных.

    Атрибуты:
        id (int): Идентификатор голосования.
        text (str): Текст голосования.
        message_id (int): Идентификатор связанного сообщения.
    """

    id: int = Field(..., title=TitleConstants.VOTING_ID)

    model_config = BASE_CONFIG


class VotingByUserBase(BaseModel):
    """
    Базовая схема для голосования пользователя.

    Определяет общие поля для схем голосования пользователя.

    Атрибуты:
        user_id (UUID): Идентификатор пользователя, участвующего в голосовании.
        voting_id (int): Идентификатор голосования.
    """

    user_id: UUID = Field(..., title=TitleConstants.VOTING_USER_ID)
    voting_id: int = Field(..., ge=1, title=TitleConstants.VOTING_ID)

    model_config = BASE_CONFIG


class VotingByUserCreate(VotingByUserBase):
    """
    Схема для голосования пользователя.

    Используется для регистрации голоса пользователя в голосовании через API.

    Атрибуты:
        user_id (UUID): Идентификатор пользователя, участвующего в голосовании.
        voting_id (int): Идентификатор голосования.
    """

    model_config = BASE_CONFIG


class VotingByUserInDB(VotingByUserBase):
    """
    Схема голосования пользователя в базе данных.

    Используется для представления данных о голосе пользователя, хранящихся в базе данных.

    Атрибуты:
        id (int): Идентификатор записи голосования.
        user_id (UUID): Идентификатор пользователя, участвующего в голосовании.
        voting_id (int): Идентификатор голосования.
    """

    id: int = Field(..., title=TitleConstants.VOTING_RECORD_ID)

    model_config = BASE_CONFIG
