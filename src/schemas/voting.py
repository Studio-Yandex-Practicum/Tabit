from uuid import UUID

from pydantic import BaseModel


class VotingBase(BaseModel):
    """Базовая модель для голосования."""

    text: str
    message_id: int


class VotingCreate(VotingBase):
    """Модель для создания голосования."""

    pass


class VotingInDB(VotingBase):
    """Модель голосования в базе данных с ID."""

    id: int


class VotingByUserCreate(BaseModel):
    """Модель для голосования пользователя."""

    user_id: UUID
    voting_id: int


class VotingByUserInDB(VotingByUserCreate):
    """Модель голосования пользователя в базе данных с ID."""

    id: int
