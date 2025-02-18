from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, field_validator, Field

from src.problems.models.enums import ColorProblem, TypeProblem, StatusProblem


class ProblemBaseSchema(BaseModel):
    """Базовая схема Проблеммы.

    Назначение:
        Определяет базовую структуру данных для проблемы.
    Параметры:
        name: Название проблемы.
        description: Описание проблемы (опционально).
        color: Цвет проблемы из перечисления ColorProblem.
        type: Тип проблемы из перечисления TypeProblem.
        status: Статус проблемы из перечисления StatusProblem.
        owner_id: UUID владельца проблемы.
    """

    name: str
    description: Optional[str] = None
    color: ColorProblem
    type: TypeProblem
    status: StatusProblem
    owner_id: UUID

    @field_validator('name')
    @classmethod
    def _validator_not_empty(cls, value: str) -> str:
        """Проверка, что значение не пустое.

        Назначение:
            Валидирует, что название проблемы не является пустой строкой.
        Параметры:
            value: Значение для валидации.
        Возвращаемое значение:
            Проверенное значение.
        Исключения:
            ValueError: Если значение пустое.
        """
        if value == '':
            raise ValueError('Name cannot be an empty string')
        return value


class ProblemResponseSchema(ProblemBaseSchema):
    """Схема Проблемы для ответа.

    Назначение:
        Определяет структуру данных для ответа с информацией о проблеме.
    Параметры:
        id: Уникальный идентификатор проблемы.
        created_at: Время создания проблемы.
        updated_at: Время последнего обновления проблемы.
    """

    id: int
    created_at: datetime
    updated_at: datetime


class ProblemCreateSchema(ProblemBaseSchema):
    """Схема для создания проблемы.

    Назначение:
        Определяет структуру данных для создания новой проблемы.
    """

    members: Optional[List[UUID]] = Field(exclude=True)


class ProblemUpdateSchema(ProblemBaseSchema):
    """Схема для обновления проблемы.

    Назначение:
        Определяет структуру данных для обновления существующей проблемы.
    Параметры:
        name: Новое название проблемы (опционально).
        description: Новое описание проблемы (опционально).
        color: Новый цвет проблемы (опционально).
        type: Новый тип проблемы (опционально).
        status: Новый статус проблемы (опционально).
        owner_id: Новый владелец проблемы (опционально).
    """

    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[ColorProblem] = None
    type: Optional[TypeProblem] = None
    status: Optional[StatusProblem] = None
    owner_id: Optional[UUID] = None
