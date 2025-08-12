from abc import ABC, abstractmethod
from typing import List

from src.models import (
    LuscherColorSecond,
    SurveyCycleForCompany,
    SurveyCycleForUser,
    SurveysStatus,
)


class RiskCriterion(ABC):
    """
    Абстрактный класс для создания групп риска.
    """

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

        from collections import defaultdict

        user_cycles_map = defaultdict(list)
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
        Критерий группы риска: Сотрудники, у которых РЕЗУЛЬТАТ последних 4 тестов — стресс.
        """
        # TODO: Понять критерии, по которым можно сопоставить == 'стресс'.
        return []


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

        # Забираем все тесты этих участников
        luscher_tests = (
            await LuscherColorSecond.filter(survey_cycle_for_user_id__in=user_cycle_ids)
            .order_by('-created_at')
            .values()
        )

        from collections import defaultdict

        luscher_map = defaultdict(list)
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
        # TODO: Получить данные социометрии за последние 4 цикла.
        # TODO: Проверить, что пользователя ни разу не выбрали.
        return []


class RiskGroupService:
    def __init__(self, criteria: List[RiskCriterion]):
        self.criteria = criteria

    async def get_full_risk_group(self, cycle: SurveyCycleForCompany) -> List[int]:
        ids = set()
        for criterion in self.criteria:
            ids.update(await criterion.get_risk_group(cycle))
        return list(ids)
