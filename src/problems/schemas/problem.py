from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem


class ProblemBaseSchema(BaseModel):
    """Базовая схема Проблеммы"""

    name: str
    description: Optional[str] = None
    color: ColorProblem
    type: TypeProblem
    status: StatusProblem
    owner_id: UUID

    @field_validator('name')
    @classmethod
    def _validator_not_empty(cls, value: str) -> str:
        """Значение не может быть пустой строкой"""
        if value == '':
            raise ValueError('Name cannot be an empty string')
        return value


class ProblemResponseSchema(ProblemBaseSchema):
    """Схема Проблемы для ответа"""

    id: int


class ProblemCreateSchema(ProblemBaseSchema):
    """Схема для создания проблемы"""

    pass


class ProblemUpdateSchema(ProblemBaseSchema):
    """Схема для обновления проблемы"""

    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[ColorProblem] = None
    type: Optional[TypeProblem] = None
    status: Optional[StatusProblem] = None
    owner_id: Optional[UUID] = None
