from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud.constants import DefaultConstants, TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models import (
    CompanyUser,
    LuscherColorFirst,
    LuscherColorSecond,
    SociometricChoice,
    SociometricCriterion,
    SociometricStrategyPreference,
    SurveyCycleForCompany,
    SurveyCycleForUser,
)
from src.schemas.sociometric import (
    SociometricChoiceCreateSchema,
    SociometricCriterionCreateSchema,
)
from src.schemas.survey import CycleForCompanyCreateSchema, CycleForCompanyUpdateSchema


class CRUDSSurveyCycleForUser(CRUDBase):
    """
    Класс для CRUD операций для циклов опросов для пользователей.
    """

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
    """
    Класс для CRUD операций для циклов опросов для компаний.
    """

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

    async def get_by_cycle_company(
        self,
        session: AsyncSession,
        cycle_company_id: int,
    ):
        """Получить все циклы пользователей для цикла компании."""
        return await self.crud_cycle_for_user._list_to_update_for_all_user_by_company(
            session, cycle_company_id
        )


class CRUDSurvey(CRUDBase):
    """
    Класс для CRUD операций для опросов.
    """

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
        cycle_for_user_id: int,
    ):
        result = await session.execute(
            select(self.model).where(self.model.survey_cycle_for_user_id == cycle_for_user_id)
        )
        return result.scalars().first()


class CRUDLuscherColor(CRUDSurvey):
    """
    Класс для CRUD операций для опроса Цветовой тест Люшера.
    """


survey_cycle_for_user_crud = CRUDSSurveyCycleForUser(SurveyCycleForUser)
survey_cycle_for_company_crud = CRUDSSurveyCycleForCompany(
    SurveyCycleForCompany,
    survey_cycle_for_user_crud,
)
luscher_color_first_crud = CRUDLuscherColor(LuscherColorFirst)
luscher_color_second_crud = CRUDLuscherColor(LuscherColorSecond)


class CRUDSociometricCriterion(CRUDBase):
    """CRUD операции для критериев социометрии."""

    async def get_by_company(
        self,
        session: AsyncSession,
        company_id: int,
    ) -> list[SociometricCriterion]:
        """Получить все критерии компании."""
        result = await session.execute(
            select(self.model).where(self.model.company_id == company_id)
        )
        return result.scalars().all()

    async def create_criterion(
        self,
        session: AsyncSession,
        criterion_in: SociometricCriterionCreateSchema,
        company_id: int,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> SociometricCriterion:
        """Создать критерий социометрии."""
        criterion_data = criterion_in.model_dump()
        criterion_data['company_id'] = company_id
        criterion_db = self.model(**criterion_data)

        try:
            session.add(criterion_db)
            if auto_commit:
                await session.commit()
                await session.refresh(criterion_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

        return criterion_db


class CRUDSociometricChoice(CRUDBase):
    """CRUD операции для социометрических выборов."""

    async def get_by_cycle_user(
        self,
        session: AsyncSession,
        cycle_user_id: int,
    ) -> list[SociometricChoice]:
        """Получить все выборы пользователя в цикле."""
        result = await session.execute(
            select(self.model).where(self.model.cycle_user_id == cycle_user_id)
        )
        return result.scalars().all()

    async def get_by_cycle_company(
        self,
        session: AsyncSession,
        cycle_company_id: int,
    ) -> list[SociometricChoice]:
        """Получить все выборы в цикле компании."""
        result = await session.execute(
            select(self.model)
            .join(SurveyCycleForUser, self.model.cycle_user_id == SurveyCycleForUser.id)
            .where(SurveyCycleForUser.survey_cycle_for_company_id == cycle_company_id)
        )
        return result.scalars().all()

    async def create_choices(
        self,
        session: AsyncSession,
        choices_in: list[SociometricChoiceCreateSchema],
        cycle_user_id: int,
        participant_id: UUID,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> list[SociometricChoice]:
        """Создать несколько социометрических выборов."""
        choices_db = []

        for choice_in in choices_in:
            choice_data = choice_in.model_dump()
            choice_data['cycle_user_id'] = cycle_user_id
            choice_data['participant_id'] = participant_id
            choice_db = self.model(**choice_data)
            choices_db.append(choice_db)

        try:
            session.add_all(choices_db)
            if auto_commit:
                await session.commit()
                for choice in choices_db:
                    await session.refresh(choice)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

        return choices_db

    async def validate_choices(
        self,
        session: AsyncSession,
        choices: list[SociometricChoiceCreateSchema],
        cycle_user_id: int,
        participant_id: UUID,
    ) -> None:
        """Валидация социометрических выборов."""
        # Получаем информацию о пользователе (проверка существования записи)
        await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

        # Группируем выборы по критериям
        choices_by_criterion = {}
        for choice in choices:
            if choice.criterion_id not in choices_by_criterion:
                choices_by_criterion[choice.criterion_id] = []
            choices_by_criterion[choice.criterion_id].append(choice)

        for criterion_id, criterion_choices in choices_by_criterion.items():
            # Получаем критерий
            criterion = await sociometric_criterion_crud.get_or_404(session, criterion_id)

            # Проверка максимального количества выборов
            if len(criterion_choices) > criterion.max_choices:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f'Превышено максимальное количество выборов для критерия '
                        f"'{criterion.name}'"
                    ),
                )

            # Проверка уникальности выбранных сотрудников
            chosen_employees = [c.chosen_employee_id for c in criterion_choices]
            if len(chosen_employees) != len(set(chosen_employees)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Дублирование выборов в критерии '{criterion.name}'",
                )

            # Проверка самоисключения
            if participant_id in chosen_employees:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Участник не может выбирать себя',
                )

            # Проверка последовательности ранжирования
            if criterion_choices[0].preference_rank is not None:
                ranks = [
                    c.preference_rank for c in criterion_choices if c.preference_rank is not None
                ]
                if len(ranks) != len(criterion_choices):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Все выборы должны иметь ранг предпочтения',
                    )
                if len(set(ranks)) != len(ranks):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Ранги предпочтения должны быть уникальными',
                    )


# Создание экземпляров CRUD
sociometric_criterion_crud = CRUDSociometricCriterion(SociometricCriterion)
sociometric_choice_crud = CRUDSociometricChoice(SociometricChoice)


class CRUDSociometricStrategyPreference(CRUDBase):
    async def upsert_preference(
        self,
        session: AsyncSession,
        cycle_user_id: int,
        strategy: str,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> SociometricStrategyPreference:
        result = await session.execute(
            select(self.model).where(self.model.cycle_user_id == cycle_user_id)
        )
        pref = result.scalars().first()
        if pref is None:
            pref = self.model(cycle_user_id=cycle_user_id, strategy=strategy)
        else:
            pref.strategy = strategy
        try:
            session.add(pref)
            if auto_commit:
                await session.commit()
                await session.refresh(pref)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return pref

    async def get_preference(
        self, session: AsyncSession, cycle_user_id: int
    ) -> SociometricStrategyPreference | None:
        result = await session.execute(
            select(self.model).where(self.model.cycle_user_id == cycle_user_id)
        )
        return result.scalars().first()


sociometric_strategy_preference_crud = CRUDSociometricStrategyPreference(
    SociometricStrategyPreference
)
