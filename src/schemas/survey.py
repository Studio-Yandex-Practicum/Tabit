from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, model_validator

from src.models.enum import LuschersColorEnum, SurveysStatus


class LuscherBaseSchema(BaseModel):
    """Базовая схема сохранения ответов теста Люшера."""

    selection_1: LuschersColorEnum
    selection_2: LuschersColorEnum
    selection_3: LuschersColorEnum
    selection_4: LuschersColorEnum
    selection_5: LuschersColorEnum
    selection_6: LuschersColorEnum
    selection_7: LuschersColorEnum
    selection_8: LuschersColorEnum


class LuscherCreateSchema(LuscherBaseSchema):
    @model_validator(mode='after')
    def validate_unique_colors(self):
        """Проверяет, что все цвета уникальны"""
        if (
            len(
                set(
                    (
                        self.selection_1,
                        self.selection_2,
                        self.selection_3,
                        self.selection_4,
                        self.selection_5,
                        self.selection_6,
                        self.selection_7,
                        self.selection_8,
                    )
                )
            )
            != 8
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Все цвета должны быть уникальными.',
            )
        return self


class LuscherResponseSchema(LuscherBaseSchema):
    """Схема для вывода сохраненных ответов теста Люшера."""

    id: int
    survey_cycle_for_user_id: int

    model_config = ConfigDict(from_attributes=True)


class CycleForUserBaseSchema(BaseModel):
    """Базовая схема цикла опросов для пользователя."""

    id: int
    user_id: UUID
    survey_cycle_for_company_id: int
    date: date
    status: SurveysStatus


class CycleForUserResponseSchema(CycleForUserBaseSchema):
    """Схема для вывода цикла опросов для пользователя."""

    model_config = ConfigDict(from_attributes=True)


class CycleForCompanyBaseSchema(BaseModel):
    """Базовая схема цикла опросов для компании."""

    date: date


class CycleForCompanyResponseSchema(CycleForCompanyBaseSchema):
    """Схема для вывода цикла опросов для компании."""

    id: int
    company_id: int
    status: SurveysStatus

    model_config = ConfigDict(from_attributes=True)


class CycleForCompanyCreateSchema(CycleForCompanyBaseSchema):
    """Схема для создания цикла опросов для компании."""

    model_config = ConfigDict(extra='forbid')


class CycleForCompanyUpdateSchema(CycleForCompanyBaseSchema):
    """Схема для изменения цикла опросов для компании."""

    status: SurveysStatus

    model_config = ConfigDict(extra='forbid')
