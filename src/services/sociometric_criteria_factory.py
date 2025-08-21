from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.constants.sociometric_criteria import (
    SociometricCategory,
    get_all_criteria,
    get_criteria_by_category,
)
from src.crud.crud_surveys import sociometric_criterion_crud
from src.models.enum import SociometricCategoryEnum
from src.schemas.sociometric import SociometricCriterionCreateSchema


class SociometricCriteriaFactory:
    """Фабрика для создания стандартных критериев социометрии."""

    @staticmethod
    async def create_default_criteria_for_company(
        session: AsyncSession, company_id: int
    ) -> List[int]:
        all_criteria = get_all_criteria()
        created_ids: List[int] = []
        for _, data in all_criteria.items():
            cat_value = getattr(data.get('category'), 'value', data.get('category'))
            category = SociometricCategoryEnum(cat_value)
            schema = SociometricCriterionCreateSchema(
                name=data['name'],
                description=data['description'],
                choice_type=data['choice_type'],
                max_choices=data['max_choices'],
                category=category,
            )
            created = await sociometric_criterion_crud.create_criterion(
                session, schema, company_id
            )
            created_ids.append(created.id)
        return created_ids

    @staticmethod
    async def create_tactical_criteria_for_company(
        session: AsyncSession, company_id: int
    ) -> List[int]:
        tactical = get_criteria_by_category(SociometricCategory.TACTICAL_LEADERSHIP)
        created_ids: List[int] = []
        for _, criteria in tactical.items():
            for _, data in criteria.items():
                schema = SociometricCriterionCreateSchema(
                    name=data['name'],
                    description=data['description'],
                    choice_type=data['choice_type'],
                    max_choices=data['max_choices'],
                    category=SociometricCategoryEnum.TACTICAL_LEADERSHIP,
                )
                created = await sociometric_criterion_crud.create_criterion(
                    session, schema, company_id
                )
                created_ids.append(created.id)
        return created_ids

    @staticmethod
    async def create_strategic_criteria_for_company(
        session: AsyncSession, company_id: int
    ) -> List[int]:
        strategic = get_criteria_by_category(SociometricCategory.STRATEGIC_LEADERSHIP)
        created_ids: List[int] = []
        for _, criteria in strategic.items():
            for _, data in criteria.items():
                schema = SociometricCriterionCreateSchema(
                    name=data['name'],
                    description=data['description'],
                    choice_type=data['choice_type'],
                    max_choices=data['max_choices'],
                    category=SociometricCategoryEnum.STRATEGIC_LEADERSHIP,
                )
                created = await sociometric_criterion_crud.create_criterion(
                    session, schema, company_id
                )
                created_ids.append(created.id)
        return created_ids
