from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Iterable, List

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import (
    LuscherColorSecond,
    RiskGroup,
    SociometricChoice,
    SurveyCycleForCompany,
    SurveyCycleForUser,
    SurveysStatus,
)
from src.models.enum import RiskGroupType

from .luscher import get_response_result


class RiskCriterion(ABC):
    """
    Абстрактный класс для создания групп риска.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Получает список ID SurveyCycleForUser, которые попадают в группу риска.
        """
        raise NotImplementedError


class NoLuscherTestsCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Сотрудники, которые не проходили ни одного теста Люшера.
        """
        query = (
            select(SurveyCycleForUser.user_id)
            .outerjoin(
                LuscherColorSecond,
                SurveyCycleForUser.id == LuscherColorSecond.survey_cycle_for_user_id,
            )
            .where(
                SurveyCycleForUser.survey_cycle_for_company_id == cycle.id,
                LuscherColorSecond.survey_cycle_for_user_id.is_(None),
            )
        )

        res = await self.session.execute(query)
        return [row[0] for row in res.all()]


class Last4NotPassedCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Сотрудники, которые не прошли последние 4 теста Люшера,
        но в прошлом проходили хотя бы один тест успешно.
        """
        completed_subquery = (
            select(SurveyCycleForUser.user_id)
            .where(SurveyCycleForUser.status == SurveysStatus.COMPLETED)
            .distinct()
            .subquery()
        )

        last4_subquery = (
            select(
                SurveyCycleForUser.user_id,
                SurveyCycleForUser.status,
                func.row_number()
                .over(
                    partition_by=SurveyCycleForUser.user_id,
                    order_by=SurveyCycleForUser.date.desc(),
                )
                .label('rn'),
            )
            .where(SurveyCycleForUser.survey_cycle_for_company_id == cycle.id)
            .subquery()
        )

        risky_subquery = (
            select(last4_subquery.c.user_id)
            .where(last4_subquery.c.rn <= 4)
            .group_by(last4_subquery.c.user_id)
            .having(func.count() == 4)
            .having(
                func.max(case((last4_subquery.c.status == SurveysStatus.COMPLETED, 1), else_=0))
                == 0
            )
            .subquery()
        )

        query = select(risky_subquery.c.user_id).where(
            risky_subquery.c.user_id.in_(select(completed_subquery.c.user_id))
        )

        result = await self.session.execute(query)
        return list(result.scalars())


class Last4PassedCriterionStress(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Сотрудники, у которых РЕЗУЛЬТАТ последних 4 тестов — стресс.
        """
        query = (
            select(SurveyCycleForUser.user_id, LuscherColorSecond)
            .join(
                LuscherColorSecond,
                SurveyCycleForUser.id == LuscherColorSecond.survey_cycle_for_user_id,
            )
            .where(SurveyCycleForUser.survey_cycle_for_company_id == cycle.id)
        )
        result = await self.session.execute(query)
        rows: list[tuple[int, LuscherColorSecond]] = result.all()

        user_luschers: dict[int, list[LuscherColorSecond]] = defaultdict(list)
        for user_id, luscher in rows:
            user_luschers[user_id].append(luscher)

        risky_users: list[int] = []

        for user_id, luschers in user_luschers.items():
            recent_tests = sorted(luschers, key=lambda test: test.created_at, reverse=True)[:4]

            if len(recent_tests) < 4:
                continue

            test_results = []
            for test in recent_tests:
                result_data = await get_response_result(self.session, test)
                test_results.append(result_data['result'])

            all_stress = all(result == 'стресс' for result in test_results)
            if all_stress:
                risky_users.append(user_id)

        return risky_users


class Last4SameLuscherOrderCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Пользователь не прошёл тест Люшера в последних 4 циклах.
        """
        user_cycles = (
            select(
                SurveyCycleForUser.id.label('cycle_id'),
                SurveyCycleForUser.user_id.label('user_id'),
                SurveyCycleForUser.date,
                func.row_number()
                .over(
                    partition_by=SurveyCycleForUser.user_id,
                    order_by=SurveyCycleForUser.date.desc(),
                )
                .label('rn'),
            )
            .where(SurveyCycleForUser.survey_cycle_for_company_id == cycle.id)
            .subquery()
        )

        last4_cycles = select(user_cycles).where(user_cycles.c.rn <= 4).subquery()

        luscher = (
            select(
                last4_cycles.c.user_id,
                last4_cycles.c.rn,
                LuscherColorSecond.color_id,
                LuscherColorSecond.position,
            )
            .join(LuscherColorSecond, LuscherColorSecond.cycle_user_id == last4_cycles.c.cycle_id)
            .subquery()
        )

        orders = (
            select(
                luscher.c.user_id,
                luscher.c.rn,
                func.array_agg(luscher.c.color_id.order_by(luscher.c.position)).label('order'),
            )
            .group_by(luscher.c.user_id, luscher.c.rn)
            .subquery()
        )

        check = (
            select(orders.c.user_id)
            .group_by(orders.c.user_id)
            .having(
                func.count().filter(
                    func.cardinality(func.array_agg(func.distinct(orders.c.order))) == 1
                )
                == 4
            )
        )

        res = await self.session.execute(check)
        return [row[0] for row in res.fetchall()]


class Last4NoSocionomySelectionCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> list[int]:
        """
        Сотрудники, которых никто не выбрал в социометрии
        за последние 4 цикла (индивидуальные для каждого пользователя).
        """

        all_cycles_subq = (
            select(
                SurveyCycleForUser.user_id,
                SurveyCycleForUser.id.label('cycle_user_id'),
                SurveyCycleForUser.date,
                func.row_number()
                .over(
                    partition_by=SurveyCycleForUser.user_id,
                    order_by=SurveyCycleForUser.date.desc(),
                )
                .label('rn'),
            )
            .where(SurveyCycleForUser.survey_cycle_for_company_id == cycle.id)
            .subquery()
        )

        last4_cycles = (
            select(all_cycles_subq.c.user_id, all_cycles_subq.c.cycle_user_id)
            .where(all_cycles_subq.c.rn <= 4)
            .subquery()
        )

        chosen_employees = (
            select(SociometricChoice.chosen_employee_id)
            .where(SociometricChoice.cycle_user_id.in_(select(last4_cycles.c.cycle_user_id)))
            .distinct()
            .subquery()
        )

        all_users_in_cycles = select(last4_cycles.c.user_id).distinct().subquery()

        query = select(all_users_in_cycles.c.user_id).where(
            all_users_in_cycles.c.user_id.not_in(select(chosen_employees.c.chosen_employee_id))
        )

        result = await self.session.execute(query)
        return result.scalars().all()


async def persist_risk_group_for_users(
    session: AsyncSession,
    user_ids: Iterable[int],
    group_type: RiskGroupType,
) -> int:
    """
    Запись результатов критерия в RiskGroup.
    Добавляем запись (user_id, group_type).
    """
    user_ids = list(dict.fromkeys(user_ids))
    if not user_ids:
        return 0

    res = await session.execute(
        select(RiskGroup.user_id)
        .where(RiskGroup.user_id.in_(user_ids))
        .where(RiskGroup.risk_group_type == group_type)
    )
    already = {row[0] for row in res.all()}

    to_insert = [uid for uid in user_ids if uid not in already]
    if not to_insert:
        return 0

    session.add_all([RiskGroup(user_id=uid, risk_group_type=group_type) for uid in to_insert])
    await session.commit()
    return len(to_insert)


class RiskGroupService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def apply_no_luscher_tests(self, cycle: SurveyCycleForCompany) -> list[int]:
        criterion = NoLuscherTestsCriterion(self.session)
        user_ids = await criterion.get_risk_group(cycle)
        await persist_risk_group_for_users(self.session, user_ids, RiskGroupType.NO_TESTS)
        return user_ids

    async def apply_last4_not_passed(self, cycle: SurveyCycleForCompany) -> list[int]:
        """
        Сохраняет пользователей, которые не прошли последние 4 теста Люшера,
        но хотя бы один раз ранее проходили успешно.
        """
        criterion = Last4NotPassedCriterion(self.session)
        user_ids = await criterion.get_risk_group(cycle)
        await persist_risk_group_for_users(
            self.session,
            user_ids,
            RiskGroupType.LAST4_NOT_PASSED,
        )
        return user_ids

    async def apply_last4_stress(self, cycle: SurveyCycleForCompany) -> list[int]:
        """
        Сохраняет пользователей, у которых последние 4 результата теста Люшера = 'стресс'.
        """
        criterion = Last4PassedCriterionStress(self.session)
        user_ids = await criterion.get_risk_group(cycle)
        await persist_risk_group_for_users(
            self.session,
            user_ids,
            RiskGroupType.STRESS_LAST4,
        )
        return user_ids

    async def apply_last4_same_order(self, cycle: SurveyCycleForCompany) -> list[int]:
        """
        Сохраняет пользователей, у которых последние 4 теста Люшера дали одинаковый порядок цветов.
        """
        criterion = Last4SameLuscherOrderCriterion(self.session)
        user_ids = await criterion.get_risk_group(cycle)
        await persist_risk_group_for_users(
            self.session,
            user_ids,
            RiskGroupType.SAME_ORDER_LAST4,
        )
        return user_ids

    async def apply_last4_no_sociometry(self, cycle: SurveyCycleForCompany) -> list[int]:
        """
        Сохраняет пользователей, которых никто не выбрал в социометрии
        """
        criterion = Last4NoSocionomySelectionCriterion(self.session)
        user_ids = await criterion.get_risk_group(cycle)
        await persist_risk_group_for_users(
            self.session,
            user_ids,
            RiskGroupType.NO_SOCIOMETRY_LAST4,
        )
        return user_ids
