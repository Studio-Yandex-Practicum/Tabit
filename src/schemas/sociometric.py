"""Схемы данных для модуля социометрии."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from src.models.enum import ChoiceType, SociometricCategoryEnum


class SociometricCriterionBaseSchema(BaseModel):
    """Базовая схема критерия социометрии."""

    name: str
    description: str
    choice_type: ChoiceType
    max_choices: int
    category: SociometricCategoryEnum


class SociometricCriterionCreateSchema(SociometricCriterionBaseSchema):
    """Схема для создания критерия социометрии."""

    model_config = ConfigDict(extra='forbid')


class SociometricCriterionUpdateSchema(SociometricCriterionBaseSchema):
    """Схема для обновления критерия социометрии."""

    model_config = ConfigDict(extra='forbid')


class SociometricCriterionResponseSchema(SociometricCriterionBaseSchema):
    """Схема для вывода критерия социометрии."""

    id: int
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class SociometricChoiceBaseSchema(BaseModel):
    """Базовая схема социометрического выбора."""

    chosen_employee_id: UUID
    criterion_id: int
    preference_rank: Optional[int] = None
    choice_type: ChoiceType


class SociometricChoiceCreateSchema(SociometricChoiceBaseSchema):
    """Схема для создания социометрического выбора."""

    @model_validator(mode='after')
    def validate_choice(self):
        """Валидация социометрического выбора."""
        if self.preference_rank is not None and self.preference_rank < 1:
            raise ValueError('Ранг предпочтения должен быть положительным')
        return self

    model_config = ConfigDict(extra='forbid')


class SociometricChoiceResponseSchema(SociometricChoiceBaseSchema):
    """Схема для вывода социометрического выбора."""

    id: int
    participant_id: UUID
    cycle_user_id: int

    model_config = ConfigDict(from_attributes=True)


class SociometricResultsSchema(BaseModel):
    """Схема результатов социометрии."""

    cycle_info: dict
    individual_scores: dict
    group_metrics: dict
    special_identifications: dict
    recommendations: list[str]

    model_config = ConfigDict(from_attributes=True)


class CombinedAnalysisSchema(BaseModel):
    """Схема комбинированного анализа Люшера и социометрии."""

    emotional_context: dict
    sociometric_results: dict
    correlations: dict
    recommendations: list[str]

    model_config = ConfigDict(from_attributes=True)
