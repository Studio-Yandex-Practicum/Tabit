from abc import ABC, abstractmethod
from typing import List

from src.business_logic.lusher import get_response_result
from src.models import (
    LuscherColorSecond,
    SociometricChoice,
    SurveyCycleForCompany,
    SurveyCycleForUser,
    SurveysStatus,
)


class RiskCriterion(ABC):
    """
    Абстрактный класс для создания групп риска."""

    @abstractmethod
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Получает список ID SurveyCycleForUser, которые попадают в группу риска.
        """
        pass


class NoLuscherTestsCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Критерий группы риска: сотрудники, которые не проходили ни одного теста Люшера.
        Возвращает:
        - Список user_id (ID участников цикла опросов), не проходивших тест Люшера.
        """
        users_in_cycle = await SurveyCycleForUser.filter(
            survey_cycle_for_company_id=cycle.id
        ).all()

        survey_cycle_for_user_ids = [user.id for user in users_in_cycle]

        luscher_user_ids = (
            await LuscherColorSecond.filter(survey_cycle_for_user_id__in=survey_cycle_for_user_ids)
            .distinct()
            .values_list('survey_cycle_for_user_id', flat=True)
        )

        luscher_user_ids_set = set(luscher_user_ids)

        risk_user_ids = [user.id for user in users_in_cycle if user.id not in luscher_user_ids_set]

        return risk_user_ids


class Last4NotPassedCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Критерий группы риска: сотрудники, которые не прошли последние 4 теста Люшера,
        но в прошлом проходили хотя бы один тест успешно.
        Возвращает:
        - Список ID участников текущего цикла (SurveyCycleForUser), попадающих под критерий.
        """
        users_in_cycle = await SurveyCycleForUser.filter(
            survey_cycle_for_company_id=cycle.id
        ).values('id', 'user_id')

        user_ids = {u['user_id'] for u in users_in_cycle}

        all_cycles = (
            await SurveyCycleForUser.filter(user_id__in=user_ids)
            .order_by('-date')
            .values('user_id', 'status')
        )

        risk_user_ids = set()

        user_cycles_map = list
        for uc in all_cycles:
            user_cycles_map[uc['user_id']].append(uc)

        for user_id, cycles in user_cycles_map.items():
            passed_exists = any(c['status'] == SurveysStatus.PASSED for c in cycles)
            if not passed_exists:
                continue

            last_4 = cycles[:4]
            if all(c['status'] != SurveysStatus.PASSED for c in last_4):
                risk_user_ids.add(user_id)

        return list(risk_user_ids)


class Last4PassedCriterionStress(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Критерий группы риска:
        Сотрудники, у которых РЕЗУЛЬТАТ последних 4 тестов — стресс.
        """

        async def get_risk_group(self, session, cycle_for_company):
            risky_user_ids = []

            for cycle_for_user in cycle_for_company.cycles_for_users:
                luscher_cycles = sorted(
                    cycle_for_user.luscher_cycles, key=lambda c: c.date_passed, reverse=True
                )

                last_four = luscher_cycles[:4]
                if len(last_four) < 4:
                    continue

                results = []
                for cycle in last_four:
                    result = await get_response_result(session, cycle)
                    results.append(result['result'])

                if all(r == 'стресс' for r in results):
                    risky_user_ids.append(cycle_for_user.user_id)

            return risky_user_ids


class Last4SameLuscherOrderCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Критерий группы риска: сотрудники, у которых в последних 4 тестах Люшера
        выбран один и тот же порядок цветов.
        Возвращает:
        - Список ID участников текущего цикла (SurveyCycleForUser),
        попадающих под данный критерий.
        """
        users_in_cycle = await SurveyCycleForUser.filter(
            survey_cycle_for_company_id=cycle.id
        ).values('id', 'user_id')

        user_cycle_ids = [u['id'] for u in users_in_cycle]
        user_id_map = {u['id']: u['user_id'] for u in users_in_cycle}

        luscher_tests = (
            await LuscherColorSecond.filter(survey_cycle_for_user_id__in=user_cycle_ids)
            .order_by('-created_at')
            .values()
        )

        luscher_map = list
        for test in luscher_tests:
            luscher_map[test['survey_cycle_for_user_id']].append(test)

        risk_user_ids = set()

        for cycle_id, tests in luscher_map.items():
            if len(tests) < 4:
                continue

            def get_order(test):
                return tuple(test[f'selection_{i}'] for i in range(1, 9))

            last4_orders = [get_order(test) for test in tests[:4]]

            if len(set(last4_orders)) == 1:
                risk_user_ids.add(user_id_map[cycle_id])

        return list(risk_user_ids)


class Last4NoSocionomySelectionCriterion(RiskCriterion):
    async def get_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        """
        Сотрудники, которых никто не выбрал в социометрии за последние 4 теста.
        """
        users_in_cycle = await SurveyCycleForUser.filter(
            survey_cycle_for_company_id=cycle.id
        ).values('id', 'user_id')

        if not users_in_cycle:
            return []

        user_cycle_map = {u['user_id']: u['id'] for u in users_in_cycle}

        all_cycles = (
            await SurveyCycleForUser.filter(user_id__in=user_cycle_map.keys())
            .order_by(SurveyCycleForUser.date)
            .values('id', 'user_id')
        )

        cycles_per_user: dict[int, List[int]] = list
        for cycle_data in all_cycles:
            user_id = cycle_data['user_id']
            if len(cycles_per_user[user_id]) < 4:
                cycles_per_user[user_id].append(cycle_data['id'])

        all_cycle_ids = [cycle_id for sublist in cycles_per_user.values() for cycle_id in sublist]

        sociometric_choices = await SociometricChoice.filter(
            cycle_user_id__in=all_cycle_ids
        ).values('chosen_employee_id', 'cycle_user_id')

        chosen_map: dict[int, set[int]] = set
        for choice in sociometric_choices:
            chosen_map[choice['cycle_user_id']].add(choice['chosen_employee_id'])

        risk_user_ids = []
        for user_id, cycle_ids in cycles_per_user.items():
            chosen_in_last4 = set()
            for cid in cycle_ids:
                chosen_in_last4.update(chosen_map.get(cid, set()))
            if user_id not in chosen_in_last4:
                risk_user_ids.append(user_id)

        return risk_user_ids


class RiskGroupService:
    def __init__(self, criteria: List[RiskCriterion]):
        self.criteria = criteria

    async def get_full_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        ids = set()
        for criterion in self.criteria:
            ids.update(await criterion.get_risk_group(cycle))
        return list(ids)
