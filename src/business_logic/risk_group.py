from abc import ABC, abstractmethod
from typing import Iterable, List

from sqlalchemy import func, select
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
        res = await self.session.execute(
            select(SurveyCycleForUser.id, SurveyCycleForUser.user_id).where(
                SurveyCycleForUser.survey_cycle_for_company_id == cycle.id
            )
        )
        cycle_user_rows: list[tuple[int, int]] = res.all()
        if not cycle_user_rows:
            return []

        cycle_for_user_ids = [r[0] for r in cycle_user_rows]
        cycle_user_to_user_id = {r[0]: r[1] for r in cycle_user_rows}

        res = await self.session.execute(
            select(LuscherColorSecond.survey_cycle_for_user_id)
            .distinct()
            .where(LuscherColorSecond.survey_cycle_for_user_id.in_(cycle_for_user_ids))
        )
        have_luscher_cycle_ids = {row[0] for row in res.all()}

        risky_user_ids = [
            cycle_user_to_user_id[cfu_id]
            for cfu_id in cycle_for_user_ids
            if cfu_id not in have_luscher_cycle_ids
        ]
        return risky_user_ids


class Last4NotPassedCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Сотрудники, которые не прошли последние 4 теста Люшера,
        но в прошлом проходили хотя бы один тест успешно.
        """
        res = await self.session.execute(
            select(SurveyCycleForUser.id, SurveyCycleForUser.user_id).where(
                SurveyCycleForUser.survey_cycle_for_company_id == cycle.id
            )
        )
        cycle_users = res.all()
        if not cycle_users:
            return []

        user_ids = {row[1] for row in cycle_users}

        res = await self.session.execute(
            select(
                SurveyCycleForUser.user_id,
                SurveyCycleForUser.status,
                SurveyCycleForUser.date,
            )
            .where(SurveyCycleForUser.user_id.in_(user_ids))
            .order_by(SurveyCycleForUser.user_id, SurveyCycleForUser.date.desc())
        )
        all_cycles = res.all()

        user_cycles: dict[int, list[tuple[str, str, str]]] = {}
        for user_id, status, date in all_cycles:
            user_cycles.setdefault(user_id, []).append({'status': status, 'date': date})

        risky_users = []
        for user_id, cycles in user_cycles.items():
            passed_exists = any(c['status'] == SurveysStatus.COMPLETED for c in cycles)
            if not passed_exists:
                continue

            last4 = cycles[:4]
            if len(last4) < 4:
                continue
            if all(c['status'] != SurveysStatus.COMPLETED for c in last4):
                risky_users.append(user_id)

        return risky_users


class Last4PassedCriterionStress(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Сотрудники, у которых РЕЗУЛЬТАТ последних 4 тестов — стресс.
        """
        risky_users: list[int] = []

        res = await self.session.execute(
            select(SurveyCycleForUser).where(
                SurveyCycleForUser.survey_cycle_for_company_id == cycle.id
            )
        )
        cycle_for_users: list[SurveyCycleForUser] = res.scalars().all()

        for cycle_for_user in cycle_for_users:
            res_luscher = await self.session.execute(
                select(LuscherColorSecond).where(
                    LuscherColorSecond.survey_cycle_for_user_id == cycle_for_user.id
                )
            )
            luscher_cycles = sorted(
                res_luscher.scalars().all(),
                key=lambda c: c.created_at,
                reverse=True,
            )

            last_four = luscher_cycles[:4]
            if len(last_four) < 4:
                continue

            results = []
            for luscher_cycle in last_four:
                result = await get_response_result(self.session, luscher_cycle)
                results.append(result['result'])

            if all(r == 'стресс' for r in results):
                risky_users.append(cycle_for_user.user_id)

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

        res = await self.session.execute(
            select(SurveyCycleForUser.user_id, SurveyCycleForUser.id).where(
                SurveyCycleForUser.survey_cycle_for_company_id == cycle.id
            )
        )
        users_in_cycle = res.all()
        if not users_in_cycle:
            return []

        res = await self.session.execute(
            select(SurveyCycleForUser.user_id, SurveyCycleForUser.id)
            .where(SurveyCycleForUser.user_id.in_([u[0] for u in users_in_cycle]))
            .order_by(SurveyCycleForUser.user_id, SurveyCycleForUser.date.desc())
        )
        all_cycles = res.all()

        cycles_per_user: dict[int, list[int]] = {}
        for user_id, cycle_user_id in all_cycles:
            cycles_per_user.setdefault(user_id, [])
            if len(cycles_per_user[user_id]) < 4:
                cycles_per_user[user_id].append(cycle_user_id)

        all_cycle_ids = [cid for sub in cycles_per_user.values() for cid in sub]

        res = await self.session.execute(
            select(SociometricChoice.chosen_employee_id).where(
                SociometricChoice.cycle_user_id.in_(all_cycle_ids)
            )
        )
        choices = res.scalars().all()

        chosen_users: set[int] = set(choices)

        risky_users: list[int] = []
        for user_id in cycles_per_user.keys():
            if user_id not in chosen_users:
                risky_users.append(user_id)

        return risky_users


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
