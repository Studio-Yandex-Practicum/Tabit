from uuid import UUID

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RiskGroupSchema(BaseModel):
    """
    Схема группы риска.

    Назначение:
        Определяет структуру данных для привязки пользователя к группе риска.
    Параметры:
        user_id: идентификатор сотрудника компании;
        risk_group_type: вид группы риска;
        created_at: Время создания проблемы;
        updated_at: Время последнего обновления проблемы.
    """
    id: int
    user_id: UUID
    risk_group_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadershipSchema(BaseModel):
    """
    Схема лидерства.

    Назначение:
        Определяет структуру данных для присвоения пользователю типа лидерства.
    Параметры:
        user_id: идентификатор сотрудника компании;
        leadership_type: вид лидерства;
        created_at: Время создания проблемы;
        updated_at: Время последнего обновления проблемы.
    """
    id: int
    user_id: UUID
    leadership_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunicationSchema(BaseModel):
    """
        Схема лидерства.

        Назначение:
            Определяет структуру данных для присвоения пользователю типа лидерства.
        Параметры:
            user_id: идентификатор сотрудника компании;
            communication_type: вид коммуникационной нагрузки;
            created_at: Время создания проблемы;
            updated_at: Время последнего обновления проблемы.
    """
    id: int
    user_id: UUID
    communication_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
