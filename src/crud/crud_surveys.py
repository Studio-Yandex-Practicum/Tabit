from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud.constants import DefaultConstants, TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models import (
    CompanyUser,
    LuscherColor,
    SurveyCycleForCompany,
    SurveyCycleForUser,
)
from src.schemas.survey import CycleForCompanyCreateSchema, CycleForCompanyUpdateSchema


class CRUDSSurveyCycleForUser(CRUDBase):
    async def _list_to_create_for_all_user_by_company(
        self,
        session: AsyncSession,
        company_id: int,
        cycle_for_company,
    ):
        list_user_from_company = await session.execute(
            select(CompanyUser).where(CompanyUser.company_id == company_id)
        )
        return [
            self.model(
                **{
                    'user_id': user.id,
                    'survey_cycle_for_company_id': cycle_for_company.id,
                    'date': cycle_for_company.date,
                    'status': cycle_for_company.status,
                }
            )
            for user in list_user_from_company.scalars().all()
        ]

    async def _list_to_update_for_all_user_by_company(
        self,
        session: AsyncSession,
        cycle_for_company_id: int,
    ):
        result = await session.execute(
            select(SurveyCycleForUser).where(
                SurveyCycleForUser.survey_cycle_for_company_id == cycle_for_company_id
            )
        )
        return result.scalars().all()


class CRUDSSurveyCycleForCompany(CRUDBase):
    def __init__(self, model, crud_cycle_for_user: CRUDSSurveyCycleForUser):
        self.crud_cycle_for_user = crud_cycle_for_user
        super().__init__(model)

    async def create_cycle(
        self,
        session: AsyncSession,
        cycle_in: CycleForCompanyCreateSchema,
        company_id: int,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ):
        cycle_survey_data = cycle_in.model_dump()
        default_data = {'company_id': company_id}
        cycle_survey_data.update(default_data)
        cycle_survey_db = self.model(**cycle_survey_data)
        try:
            session.add(cycle_survey_db)
            await session.flush()
            list_cycles_for_users = (
                await self.crud_cycle_for_user._list_to_create_for_all_user_by_company(
                    session,
                    company_id,
                    cycle_survey_db,
                )
            )
            session.add_all(list_cycles_for_users)
            if auto_commit:
                await session.commit()
                await session.refresh(cycle_survey_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return cycle_survey_db

    async def update_cycle(
        self,
        session: AsyncSession,
        cycle_db: SurveyCycleForCompany,
        cycle_in: CycleForCompanyUpdateSchema,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ):
        cycle_data = jsonable_encoder(cycle_db)
        update_data = cycle_in.model_dump(exclude_unset=True)
        for field in cycle_data:
            if field in update_data:
                setattr(cycle_db, field, update_data[field])

        try:
            session.add(cycle_db)
            await session.flush()
            list_cycles_for_users = (
                await self.crud_cycle_for_user._list_to_update_for_all_user_by_company(
                    session,
                    cycle_db.id,
                )
            )
            for cycles_for_users in list_cycles_for_users:
                for field in ('status', 'date'):
                    if field in update_data:
                        setattr(cycles_for_users, field, update_data[field])
            session.add_all(list_cycles_for_users)
            if auto_commit:
                await session.commit()
                await session.refresh(cycle_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.UPDATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return cycle_db

    async def get_by_week_number(
        self,
        session: AsyncSession,
        week_number: int,
        company_id: int,
    ):
        result = await session.execute(
            select(self.model).where(
                and_(
                    extract('week', self.model.date) == week_number,
                    self.model.company_id == company_id,
                )
            )
        )
        return result.scalars().all()


class CRUDSurvey(CRUDBase):
    async def create_survey(
        self,
        session: AsyncSession,
        survey_in,
        cycle_for_user: int,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ):
        survey_data = survey_in.model_dump()
        default_data = {'survey_cycle_for_user_id': cycle_for_user}
        survey_data.update(default_data)
        survey_db = self.model(**survey_data)
        try:
            session.add(survey_db)
            if auto_commit:
                await session.commit()
                await session.refresh(survey_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return survey_db

    async def get_by_cycle(
        self,
        session: AsyncSession,
        cycle_for_user: int,
    ):
        result = await session.execute(
            select(self.model).where(self.model.survey_cycle_for_user_id == cycle_for_user)
        )
        return result.scalars().first()


class CRUDLuscherColor(CRUDSurvey):
    pass


survey_cycle_for_user_crud = CRUDSSurveyCycleForUser(SurveyCycleForUser)
survey_cycle_for_company_crud = CRUDSSurveyCycleForCompany(
    SurveyCycleForCompany,
    survey_cycle_for_user_crud,
)
luscher_color_crud = CRUDLuscherColor(LuscherColor)
