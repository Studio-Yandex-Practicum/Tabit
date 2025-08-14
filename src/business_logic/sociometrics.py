"""Бизнес-логика модуля социометрии для Tabit."""

from typing import Any, Dict, List, Literal, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud.crud_surveys import (
    luscher_color_first_crud,
    luscher_color_second_crud,
    sociometric_choice_crud,
    survey_cycle_for_company_crud,
    survey_cycle_for_user_crud,
)
from src.crud.crud_user import user_crud
from src.models.enum import ChoiceType


async def check_user_is_moderator(session: AsyncSession, user_id: UUID, company_id: int) -> bool:
    """
    Проверить, является ли пользователь модератором компании.

    Использует CRUD операции вместо прямых запросов к БД.

    Args:
        session: Сессия базы данных
        user_id: ID пользователя
        company_id: ID компании

    Returns:
        bool: True если пользователь является модератором компании
    """
    return await user_crud.is_user_moderator(session, user_id, company_id)


class SociometricIndices:
    """Класс для расчета социометрических индексов."""

    @staticmethod
    def calculate_sociometric_indices(
        choices_data: List[Any],
        calculation_type: Literal[
            'popularity',
            'rejection',
            'expansiveness',
            'mutual_choices',
            'group_cohesion',
            'sociometric_report',
            'all',
        ] = 'all',
        total_participants: int = None,
    ) -> Dict:
        """
        Единый метод для расчета социометрических индексов.

        Args:
            choices_data: Список словарей с данными выборов
            calculation_type: Тип расчета ('popularity', 'rejection', 'expansiveness',
                           'mutual_choices', 'group_cohesion', 'sociometric_report', 'all')
            total_participants: Общее количество участников (нужно для group_cohesion)

        Returns:
            Словарь с результатами расчетов в зависимости от типа
        """

        def _get(obj, attr):
            return obj.get(attr) if isinstance(obj, dict) else getattr(obj, attr, None)

        if calculation_type == 'all' or calculation_type == 'sociometric_report':
            # Выполняем все расчеты за один проход
            popularity_scores = {}
            rejection_scores = {}
            expansiveness_scores = {}
            choices_dict = {}

            # Один проход по всем данным
            for choice in choices_data:
                participant_id = _get(choice, 'participant_id')
                chosen_employee_id = _get(choice, 'chosen_employee_id')
                choice_type = _get(choice, 'choice_type')

                # Расчет экспансивности (количество сделанных выборов)
                if participant_id:
                    expansiveness_scores[participant_id] = (
                        expansiveness_scores.get(participant_id, 0) + 1
                    )

                # Расчет популярности и отторжения
                if chosen_employee_id:
                    if choice_type == ChoiceType.POSITIVE:
                        popularity_scores[chosen_employee_id] = (
                            popularity_scores.get(chosen_employee_id, 0) + 1
                        )
                    elif choice_type == ChoiceType.NEGATIVE:
                        rejection_scores[chosen_employee_id] = (
                            rejection_scores.get(chosen_employee_id, 0) + 1
                        )

                # Подготовка для расчета взаимных выборов
                if participant_id and chosen_employee_id:
                    key = (participant_id, chosen_employee_id)
                    choices_dict[key] = choice

            # Расчет взаимных выборов
            mutual_pairs = []
            for key, choice in choices_dict.items():
                participant_id, chosen_employee_id = key
                choice_type = _get(choice, 'choice_type')

                reverse_key = (chosen_employee_id, participant_id)
                if reverse_key in choices_dict:
                    reverse_choice = choices_dict[reverse_key]
                    if (
                        choice_type == ChoiceType.POSITIVE
                        and reverse_choice.get('choice_type') == ChoiceType.POSITIVE
                    ):
                        mutual_pairs.append((key, reverse_key))

            # Расчет сплоченности группы
            group_cohesion = 0.0
            if total_participants and total_participants > 1:
                total_possible_choices = total_participants * (total_participants - 1)
                actual_positive_choices = len(
                    [c for c in choices_data if _get(c, 'choice_type') == ChoiceType.POSITIVE]
                )
                group_cohesion = (
                    actual_positive_choices / total_possible_choices
                    if total_possible_choices > 0
                    else 0.0
                )

            if calculation_type == 'sociometric_report':
                return {
                    'popularity': popularity_scores,
                    'rejection': rejection_scores,
                    'expansiveness': expansiveness_scores,
                    'mutual_choices': mutual_pairs,
                    'group_cohesion': group_cohesion,
                    'total_participants': total_participants,
                }
            else:  # 'all'
                return {
                    'popularity': popularity_scores,
                    'rejection': rejection_scores,
                    'expansiveness': expansiveness_scores,
                    'mutual_choices': mutual_pairs,
                    'group_cohesion': group_cohesion,
                }

        elif calculation_type == 'popularity':
            popularity_scores = {}
            for choice in choices_data:
                if _get(choice, 'choice_type') == ChoiceType.POSITIVE:
                    chosen_employee_id = _get(choice, 'chosen_employee_id')
                    if chosen_employee_id:
                        popularity_scores[chosen_employee_id] = (
                            popularity_scores.get(chosen_employee_id, 0) + 1
                        )
            return {'popularity': popularity_scores}

        elif calculation_type == 'rejection':
            rejection_scores = {}
            for choice in choices_data:
                if _get(choice, 'choice_type') == ChoiceType.NEGATIVE:
                    chosen_employee_id = _get(choice, 'chosen_employee_id')
                    if chosen_employee_id:
                        rejection_scores[chosen_employee_id] = (
                            rejection_scores.get(chosen_employee_id, 0) + 1
                        )
            return {'rejection': rejection_scores}

        elif calculation_type == 'expansiveness':
            expansiveness_scores = {}
            for choice in choices_data:
                participant_id = _get(choice, 'participant_id')
                if participant_id:
                    expansiveness_scores[participant_id] = (
                        expansiveness_scores.get(participant_id, 0) + 1
                    )
            return {'expansiveness': expansiveness_scores}

        elif calculation_type == 'mutual_choices':
            mutual_pairs = []
            choices_dict = {}

            for choice in choices_data:
                participant_id = _get(choice, 'participant_id')
                chosen_employee_id = _get(choice, 'chosen_employee_id')
                choice_type = _get(choice, 'choice_type')

                if participant_id and chosen_employee_id:
                    key = (participant_id, chosen_employee_id)
                    choices_dict[key] = choice

                    reverse_key = (chosen_employee_id, participant_id)
                    if reverse_key in choices_dict:
                        reverse_choice = choices_dict[reverse_key]
                        if (
                            choice_type == ChoiceType.POSITIVE
                            and _get(reverse_choice, 'choice_type') == ChoiceType.POSITIVE
                        ):
                            mutual_pairs.append((key, reverse_key))

            return {'mutual_choices': mutual_pairs}

        elif calculation_type == 'group_cohesion':
            if not total_participants or total_participants <= 1:
                return {'group_cohesion': 0.0}

            total_possible_choices = total_participants * (total_participants - 1)
            actual_positive_choices = len(
                [c for c in choices_data if _get(c, 'choice_type') == ChoiceType.POSITIVE]
            )
            group_cohesion = (
                actual_positive_choices / total_possible_choices
                if total_possible_choices > 0
                else 0.0
            )
            return {'group_cohesion': group_cohesion}

        else:
            raise ValueError(f'Неизвестный тип расчета: {calculation_type}')

    # Оставляем старые методы для обратной совместимости
    @staticmethod
    def calculate_popularity(choices_data: List[Dict]) -> Dict[UUID, int]:
        """Расчет популярности (степень входа)."""
        result = SociometricIndices.calculate_sociometric_indices(choices_data, 'popularity')
        return result['popularity']

    @staticmethod
    def calculate_rejection(choices_data: List[Dict]) -> Dict[UUID, int]:
        """Расчет отторжения (отрицательная степень входа)."""
        result = SociometricIndices.calculate_sociometric_indices(choices_data, 'rejection')
        return result['rejection']

    @staticmethod
    def calculate_expansiveness(choices_data: List[Dict]) -> Dict[UUID, int]:
        """Расчет экспансивности (степень выхода)."""
        result = SociometricIndices.calculate_sociometric_indices(choices_data, 'expansiveness')
        return result['expansiveness']

    @staticmethod
    def calculate_mutual_choices(choices_data: List[Dict]) -> List[Tuple]:
        """Расчет взаимных выборов."""
        result = SociometricIndices.calculate_sociometric_indices(choices_data, 'mutual_choices')
        return result['mutual_choices']

    @staticmethod
    def calculate_group_cohesion(choices_data: List[Dict], total_participants: int) -> float:
        """Расчет сплоченности группы."""
        result = SociometricIndices.calculate_sociometric_indices(
            choices_data, 'group_cohesion', total_participants
        )
        return result['group_cohesion']


def identify_sociometric_stars_and_isolates(
    popularity_scores: Dict[UUID, int], rejection_scores: Dict[UUID, int], threshold: float = 0.3
) -> Dict[str, List[Dict]]:
    """Выявление социометрических звезд и изолятов.

    Args:
        popularity_scores: Словарь популярности участников
        rejection_scores: Словарь отторжения участников
        threshold: Порог для определения звезд (по умолчанию 30%)

    Returns:
        Словарь с ключами 'stars' и 'isolates', содержащий списки участников
    """
    total_participants = len(popularity_scores) if popularity_scores else 0
    if total_participants == 0:
        return {'stars': [], 'isolates': []}

    stars = []
    isolates = []

    # Объединяем всех участников
    all_participants = set(popularity_scores.keys()) | set(rejection_scores.keys())

    for employee_id in all_participants:
        popularity = popularity_scores.get(employee_id, 0)
        rejection = rejection_scores.get(employee_id, 0)
        net_score = popularity - rejection

        # Звезды: высокий положительный баланс
        if net_score >= total_participants * threshold:
            stars.append(
                {
                    'employee_id': employee_id,
                    'popularity': popularity,
                    'rejection': rejection,
                    'net_score': net_score,
                }
            )

        # Изоляты: низкий или отрицательный баланс
        if net_score <= 0 or (popularity == 0 and rejection == 0):
            isolates.append(
                {
                    'employee_id': employee_id,
                    'popularity': popularity,
                    'rejection': rejection,
                    'net_score': net_score,
                }
            )

    return {'stars': stars, 'isolates': isolates}


async def analyze_emotional_context(session: AsyncSession, cycle_user_id: int) -> Dict[str, str]:
    """Анализ эмоционального контекста перед социометрией.

    Args:
        session: Сессия базы данных
        cycle_user_id: ID цикла пользователя

    Returns:
        Словарь с анализом эмоционального состояния
    """
    try:
        luscher_first = await luscher_color_first_crud.get_by_cycle(session, cycle_user_id)
        if not luscher_first:
            return {
                'stress_level': 'Не определен',
                'emotional_state': 'Не определен',
                'social_readiness': 'Не определен',
            }

        # Получаем статус из существующей логики Люшера
        from src.business_logic.luscher import get_set_answer, get_status_luscher

        set_answer = await get_set_answer(session, cycle_user_id)
        status = get_status_luscher(set_answer)

        # Определяем готовность к социальному взаимодействию
        if 'Воодушевлен' in status or 'В норме' in status:
            social_readiness = 'Высокая'
        elif 'Низкий уровень стресса' in status:
            social_readiness = 'Средняя'
        else:
            social_readiness = 'Низкая'

        return {
            'stress_level': status,
            'emotional_state': status,
            'social_readiness': social_readiness,
        }

    except Exception as e:
        logger.error(f'Ошибка при анализе эмоционального контекста: {e}')
        return {
            'stress_level': 'Ошибка анализа',
            'emotional_state': 'Ошибка анализа',
            'social_readiness': 'Ошибка анализа',
        }


async def analyze_emotional_context_for_cycle(
    session: AsyncSession, cycle_company_id: int
) -> dict:
    """Агрегированный анализ эмоционального контекста по всем пользователям цикла."""
    try:
        # Получаем всех пользователей в цикле
        cycle_users = await survey_cycle_for_company_crud.get_by_cycle_company(
            session, cycle_company_id
        )
        summaries: List[Dict[str, str]] = []
        for cu in cycle_users:
            summary = await analyze_emotional_context(session, cu.id)
            summaries.append(summary)

        def count_by(key: str) -> Dict[str, int]:
            res: Dict[str, int] = {}
            for s in summaries:
                val = s.get(key, 'Не определен')
                res[val] = res.get(val, 0) + 1
            return res

        total = len(summaries)
        return {
            'total_users': total,
            'stress_level_distribution': count_by('stress_level'),
            'emotional_state_distribution': count_by('emotional_state'),
            'social_readiness_distribution': count_by('social_readiness'),
        }
    except Exception as e:
        logger.error(f'Ошибка при анализе эмоционального контекста цикла: {e}')
        return {
            'total_users': 0,
            'stress_level_distribution': {},
            'emotional_state_distribution': {},
            'social_readiness_distribution': {},
        }


async def correlate_emotions_with_sociometric_choices(
    session: AsyncSession, cycle_company_id: int
) -> dict:
    """Простая корреляция эмоционального состояния с социометрическими показателями."""
    try:
        # Получаем выборы и участников
        from src.crud.crud_surveys import sociometric_choice_crud

        choices = await sociometric_choice_crud.get_by_cycle_company(session, cycle_company_id)
        cycle_users = await survey_cycle_for_company_crud.get_by_cycle_company(
            session, cycle_company_id
        )
        participant_ids = [cu.user_id for cu in cycle_users]

        # Индексы по участникам
        indices = SociometricIndices.calculate_sociometric_indices(
            choices, 'all', total_participants=len(participant_ids)
        )
        popularity = indices['popularity']
        rejection = indices['rejection']
        expansiveness = indices['expansiveness']

        # Эмоциональные статусы по пользователям
        emotion_map: Dict[UUID, Dict[str, str]] = {}
        for cu in cycle_users:
            emotion_map[cu.user_id] = await analyze_emotional_context(session, cu.id)

        # Условные “оценки” эмоций для грубой корреляции
        def readiness_score(v: str) -> int:
            if 'Высок' in v:
                return 2
            if 'Средн' in v:
                return 1
            return 0

        def stress_score(v: str) -> int:
            if 'Высок' in v:
                return 2
            if 'Низк' in v:
                return 0
            return 1

        # Собираем массивы для сравнения
        data = []
        for uid in participant_ids:
            emo = emotion_map.get(uid, {})
            data.append(
                {
                    'user_id': uid,
                    'social_readiness_score': readiness_score(emo.get('social_readiness', '')),
                    'stress_score': stress_score(emo.get('stress_level', '')),
                    'popularity': popularity.get(uid, 0),
                    'rejection': rejection.get(uid, 0),
                    'expansiveness': expansiveness.get(uid, 0),
                }
            )

        # Простые сводки влияния
        def avg(iterable: List[int]) -> float:
            return sum(iterable) / len(iterable) if iterable else 0.0

        stress_impact = {
            'avg_popularity_by_stress': {
                'low_or_normal': avg([d['popularity'] for d in data if d['stress_score'] <= 1]),
                'high': avg([d['popularity'] for d in data if d['stress_score'] == 2]),
            },
            'avg_rejection_by_stress': {
                'low_or_normal': avg([d['rejection'] for d in data if d['stress_score'] <= 1]),
                'high': avg([d['rejection'] for d in data if d['stress_score'] == 2]),
            },
        }

        stars_isolates = identify_sociometric_stars_and_isolates(popularity, rejection)
        social_position_impact = {
            'stars_readiness_avg': avg(
                [
                    readiness_score(
                        emotion_map.get(u['employee_id'], {}).get('social_readiness', '')
                    )
                    for u in stars_isolates['stars']
                ]
            ),
            'isolates_stress_avg': avg(
                [
                    stress_score(emotion_map.get(u['employee_id'], {}).get('stress_level', ''))
                    for u in stars_isolates['isolates']
                ]
            ),
        }

        isolation_effects = {
            'high_stress_isolate_rate': (
                len(
                    [
                        u
                        for u in stars_isolates['isolates']
                        if stress_score(
                            emotion_map.get(u['employee_id'], {}).get('stress_level', '')
                        )
                        == 2
                    ]
                )
                / max(1, len(stars_isolates['isolates']))
            )
        }

        return {
            'stress_impact_on_choices': stress_impact,
            'social_position_impact': social_position_impact,
            'isolation_effects': isolation_effects,
        }

    except Exception as e:
        logger.error(f'Ошибка при корреляционном анализе: {e}')
        return {
            'stress_impact_on_choices': {},
            'social_position_impact': {},
            'isolation_effects': {},
        }


def generate_combined_recommendations(
    emotional_context: dict, sociometric_results: dict, correlations: dict
) -> list[str]:
    """Генерация комбинированных рекомендаций (заглушка)."""
    # TODO: Реализовать генерацию комбинированных рекомендаций
    return ['Комбинированный анализ находится в разработке']


async def compare_emotional_changes(session: AsyncSession, cycle_user_id: int) -> Dict[str, Dict]:
    """Сравнение эмоционального состояния до и после социометрии.

    Args:
        session: Сессия базы данных
        cycle_user_id: ID цикла пользователя

    Returns:
        Словарь с сравнением эмоциональных состояний
    """
    try:
        luscher_first = await luscher_color_first_crud.get_by_cycle(session, cycle_user_id)
        luscher_second = await luscher_color_second_crud.get_by_cycle(session, cycle_user_id)

        if not luscher_first or not luscher_second:
            return {
                'before_sociometry': {'status': 'Не определен'},
                'after_sociometry': {'status': 'Не определен'},
                'changes': 'Недостаточно данных для сравнения',
            }

        # Анализируем состояния до и после
        before_analysis = await analyze_emotional_context(session, cycle_user_id)

        # Для анализа "после" используем второй тест Люшера
        from src.business_logic.luscher import get_set_answer, get_status_luscher

        # Получаем статус второго теста
        set_answer_second = await get_set_answer(session, cycle_user_id)
        status_after = get_status_luscher(set_answer_second)

        after_analysis = {
            'stress_level': status_after,
            'emotional_state': status_after,
            'social_readiness': 'Высокая'
            if 'Воодушевлен' in status_after or 'В норме' in status_after
            else 'Средняя',
        }

        # Определяем изменения
        changes = calculate_emotional_changes(before_analysis, after_analysis)

        return {
            'before_sociometry': before_analysis,
            'after_sociometry': after_analysis,
            'changes': changes,
        }

    except Exception as e:
        logger.error(f'Ошибка при сравнении эмоциональных изменений: {e}')
        return {
            'before_sociometry': {'status': 'Ошибка анализа'},
            'after_sociometry': {'status': 'Ошибка анализа'},
            'changes': 'Ошибка при анализе изменений',
        }


def calculate_emotional_changes(
    before_analysis: Dict[str, str], after_analysis: Dict[str, str]
) -> str:
    """Расчет изменений эмоционального состояния.

    Args:
        before_analysis: Анализ состояния до социометрии
        after_analysis: Анализ состояния после социометрии

    Returns:
        Описание изменений
    """
    before_stress = before_analysis.get('stress_level', '')
    after_stress = after_analysis.get('stress_level', '')

    if 'Воодушевлен' in before_stress and 'Воодушевлен' in after_stress:
        return 'Стабильное позитивное состояние'
    elif 'Воодушевлен' in before_stress and 'В норме' in after_stress:
        return 'Незначительное снижение позитивного настроения'
    elif 'В норме' in before_stress and 'Воодушевлен' in after_stress:
        return 'Улучшение эмоционального состояния'
    elif 'Высокий уровень стресса' in before_stress and 'Низкий уровень стресса' in after_stress:
        return 'Значительное улучшение - снижение стресса'
    elif 'Низкий уровень стресса' in before_stress and 'Высокий уровень стресса' in after_stress:
        return 'Ухудшение состояния - повышение стресса'
    elif 'Высокий уровень стресса' in before_stress and 'Высокий уровень стресса' in after_stress:
        return 'Стабильно высокий уровень стресса'
    else:
        return 'Смешанные изменения в эмоциональном состоянии'


async def validate_sociometric_choices(
    session: AsyncSession, choices_data: List[Dict], cycle_user_id: int, criteria_data: List[Dict]
) -> None:
    """Валидация социометрических выборов.

    Args:
        session: Сессия базы данных
        choices_data: Данные выборов для валидации
        cycle_user_id: ID цикла пользователя
        criteria_data: Данные критериев социометрии

    Raises:
        HTTPException: При нарушении правил валидации
    """
    try:
        # Получаем информацию о пользователе
        cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
        participant_id = cycle_user.user_id

        # Группируем выборы по критериям
        choices_by_criterion = {}
        for choice in choices_data:
            criterion_id = choice.get('criterion_id')
            if criterion_id not in choices_by_criterion:
                choices_by_criterion[criterion_id] = []
            choices_by_criterion[criterion_id].append(choice)

        # Создаем словарь критериев для быстрого доступа
        criteria_dict = {c.get('id'): c for c in criteria_data}

        for criterion_id, criterion_choices in choices_by_criterion.items():
            criterion = criteria_dict.get(criterion_id)
            if not criterion:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Критерий с ID {criterion_id} не найден',
                )

            # Проверка максимального количества выборов
            max_choices = criterion.get('max_choices', 3)
            if len(criterion_choices) > max_choices:
                criterion_name = criterion.get('name', 'Неизвестный критерий')
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Превышено максимальное количество выборов для критерия '
                    f"'{criterion_name}'",
                )

            # Проверка уникальности выбранных сотрудников
            chosen_employees = [c.get('chosen_employee_id') for c in criterion_choices]
            if len(chosen_employees) != len(set(chosen_employees)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Дублирование выборов в критерии '{criterion.get('name')}'",
                )

            # Проверка самоисключения
            if participant_id in chosen_employees:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Участник не может выбирать себя',
                )

            # Проверка последовательности ранжирования
            choices_with_rank = [
                c for c in criterion_choices if c.get('preference_rank') is not None
            ]
            if choices_with_rank:
                if len(choices_with_rank) != len(criterion_choices):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Все выборы должны иметь ранг предпочтения',
                    )
                ranks = [c.get('preference_rank') for c in choices_with_rank]
                if len(set(ranks)) != len(ranks):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Ранги предпочтения должны быть уникальными',
                    )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Ошибка при валидации социометрических выборов: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка при валидации выборов',
        )


async def generate_sociometric_report(session: AsyncSession, cycle_company_id: int) -> dict:
    """Генерация полного отчета по социометрии."""

    # Получаем все данные
    choices_data = await sociometric_choice_crud.get_by_cycle_company(session, cycle_company_id)

    # Получаем участников цикла
    from src.crud.crud_surveys import survey_cycle_for_company_crud

    cycle_users = await survey_cycle_for_company_crud.get_by_cycle_company(
        session, cycle_company_id
    )
    participants = [cycle_user.user_id for cycle_user in cycle_users]

    # Рассчитываем индексы
    popularity_scores = SociometricIndices.calculate_popularity(choices_data)
    rejection_scores = SociometricIndices.calculate_rejection(choices_data)
    expansiveness_scores = SociometricIndices.calculate_expansiveness(choices_data)
    mutual_choices = SociometricIndices.calculate_mutual_choices(choices_data)
    group_cohesion = SociometricIndices.calculate_group_cohesion(choices_data, len(participants))

    # Выявляем звезд и изолятов
    stars_and_isolates = identify_sociometric_stars_and_isolates(
        popularity_scores, rejection_scores
    )

    return {
        'cycle_info': {
            'cycle_company_id': cycle_company_id,
            'total_participants': len(participants),
            'total_choices': len(choices_data),
        },
        'individual_scores': {
            'popularity': popularity_scores,
            'rejection': rejection_scores,
            'expansiveness': expansiveness_scores,
        },
        'group_metrics': {
            'cohesion': group_cohesion,
            'mutual_choices_count': len(mutual_choices),
            'stars_count': len(stars_and_isolates['stars']),
            'isolates_count': len(stars_and_isolates['isolates']),
        },
        'special_identifications': stars_and_isolates,
        'recommendations': generate_recommendations(
            popularity_scores, rejection_scores, stars_and_isolates, group_cohesion
        ),
    }


def generate_recommendations(
    popularity_scores: dict,
    rejection_scores: dict,
    stars_and_isolates: dict,
    group_cohesion: float,
) -> list[str]:
    """Генерация рекомендаций для HR на основе социометрических данных."""

    recommendations = []

    # Анализ изолятов
    if stars_and_isolates['isolates']:
        recommendations.append(
            'Выявлены социально изолированные сотрудники. '
            'Рекомендуется провести индивидуальные беседы и '
            'разработать программы интеграции.'
        )

    # Анализ звезд
    if stars_and_isolates['stars']:
        recommendations.append(
            'Выявлены неформальные лидеры. '
            'Рекомендуется привлечь их к наставничеству '
            'и развитию командных навыков.'
        )

    # Анализ сплоченности
    if group_cohesion < 0.3:
        recommendations.append(
            'Низкая сплоченность группы. Рекомендуется провести тимбилдинг мероприятия.'
        )
    elif group_cohesion > 0.7:
        recommendations.append(
            'Высокая сплоченность группы. Можно использовать для сложных проектов.'
        )

    # Анализ отторжения
    high_rejection = [emp_id for emp_id, score in rejection_scores.items() if score > 2]
    if high_rejection:
        recommendations.append(
            'Выявлены сотрудники с высоким уровнем отторжения. '
            'Рекомендуется провести конфликтологический анализ.'
        )

    return recommendations


async def get_user_test_completion_status(
    session: AsyncSession, cycle_user_id: int, is_moderator: bool = False
) -> Dict[str, any]:
    """Получить статус завершения теста для пользователя.

    Args:
        session: Сессия базы данных
        cycle_user_id: ID цикла пользователя
        is_moderator: Является ли пользователь модератором

    Returns:
        Словарь со статусом завершения теста
    """
    try:
        # Получаем прогресс теста из фактических данных
        cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
        cycle_company = await survey_cycle_for_company_crud.get_or_404(
            session, cycle_user.survey_cycle_for_company_id
        )

        from src.crud.crud_surveys import sociometric_choice_crud, sociometric_criterion_crud

        all_criteria = await sociometric_criterion_crud.get_by_company(
            session, company_id=cycle_company.company_id
        )
        total_criteria = len(all_criteria)

        answered_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
        answered_criteria = list({choice.criterion_id for choice in answered_choices})
        answered_count = len(answered_criteria)
        progress_percentage = (answered_count / total_criteria) * 100 if total_criteria > 0 else 0

        # Определяем минимальный порог завершения теста
        # Модераторы не проходят тесты - они их создают и управляют
        min_percentage = 100.0
        can_complete = progress_percentage >= min_percentage

        return {
            'total_questions': total_criteria,
            'answered_questions': answered_count,
            'remaining_questions': total_criteria - answered_count,
            'progress_percentage': progress_percentage,
            'min_required_percentage': min_percentage,
            'can_complete_test': can_complete,
            'is_moderator': is_moderator,
            'completion_message': (
                'Тест завершен'
                if can_complete
                else f'Необходимо ответить еще на {total_criteria - answered_count} вопросов'
            ),
        }

    except Exception as e:
        logger.error(f'Ошибка при получении статуса завершения теста: {e}')
        return {
            'total_questions': 0,
            'answered_questions': 0,
            'remaining_questions': 0,
            'progress_percentage': 0,
            'min_required_percentage': 100.0,
            'can_complete_test': False,
            'is_moderator': is_moderator,
            'completion_message': 'Ошибка при получении статуса',
        }


async def get_user_strategy_restrictions(is_moderator: bool) -> Dict[str, any]:
    """Получить ограничения стратегий для пользователя.

    Args:
        is_moderator: Является ли пользователь модератором

    Returns:
        Словарь с ограничениями стратегий
    """
    if is_moderator:
        return {
            'available_strategies': [
                'balanced',
                'category_focused',
                'type_focused',
                'random',
                'adaptive',
            ],
            'default_strategy': 'balanced',
            'can_change_strategy': True,
            'can_use_preferences': True,
        }
    else:
        return {
            'available_strategies': ['balanced'],
            'default_strategy': 'balanced',
            'can_change_strategy': False,
            'can_use_preferences': False,
        }


# Константы для интерпретации результатов
INTERPRETATION_WARNINGS = [
    'Результаты социометрии отражают восприятие на момент тестирования',
    'Эмоциональное состояние может влиять на социальные выборы',
    'Необходимо учитывать контекст и другие факторы',
    'Избегайте упрощенных интерпретаций и навешивания ярлыков',
]

SOCIOMETRIC_RULES = {
    'self_exclusion': 'Участник не может выбирать себя',
    'max_choices_per_criterion': 'Максимальное количество выборов по критерию',
    'unique_choices': 'Уникальность выборов в рамках критерия',
    'ranking_consistency': 'Последовательность ранжирования',
}
