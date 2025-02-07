from pydantic import BaseModel
from uuid import UUID


class MessageBase(BaseModel):
    """Базовая модель для сообщений в ленте."""
    text: str
    important: bool
    problem_id: int
    owner_id: UUID


class MessageCreate(MessageBase):
    """Модель для создания нового сообщения в ленте."""
    pass


class MessageInDB(MessageBase):
    """Модель сообщения в базе данных с ID."""
    id: int


class CommentBase(BaseModel):
    """Базовая модель для комментариев."""
    text: str
    message_id: int
    owner_id: UUID


class CommentCreate(CommentBase):
    """Модель для создания комментария."""
    pass


class CommentInDB(CommentBase):
    """Модель комментария в базе данных с ID."""
    id: int


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
