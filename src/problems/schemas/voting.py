from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VotingBase(BaseModel):
    """
    Параметры:
        text: текст голосования.
        message_id: идентефикатор треда.
    """

    text: str
    message_id: int

    model_config = ConfigDict(
        title='Базовая схема голосования', description='Базовая схема для голосования'
    )


class VotingCreate(VotingBase):
    """Модель для создания голосования."""

    model_config = ConfigDict(
        title='Схема создания голосования', description='Схема для создания голосования'
    )


class VotingInDB(VotingBase):
    """
    Параметры:
        id: идентефикатор.
    """

    id: int

    model_config = ConfigDict(
        title='Схема голосования для бд', description='Модель голосования в базе данных с ID.'
    )


class VotingByUserCreate(BaseModel):
    """
    Параметры:
        user_id: id голосовавшего пользователя.
        voting_id: идентификатор варианта голосования.
    """

    user_id: UUID
    voting_id: int

    model_config = ConfigDict(
        title='Схема голосования', description='Схема для голосования пользователя'
    )


class VotingByUserInDB(VotingByUserCreate):
    """
    Параметры:
        id: идентефикатор.
    """

    id: int

    model_config = ConfigDict(
        title='Схема для голосования пользователя',
        description='Модель голосования пользователя в базе данных с ID.',
    )
