"""Бизнес-логика модуля социометрии для Tabit."""

from typing import Dict, List, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud.crud_surveys import (
    luscher_color_first_crud,
    luscher_color_second_crud,
    survey_cycle_for_user_crud,
)
from src.models.enum import ChoiceType


class SociometricIndices:
    """Класс для расчета социометрических индексов."""

    @staticmethod
    def calculate_popularity(choices_data: List[Dict]) -> Dict[UUID, int]:
        """Расчет популярности (степень входа).

        Args:
            choices_data: Список словарей с данными выборов

        Returns:
            Словарь {employee_id: количество_положительных_выборов}
        """
        popularity_scores = {}
        for choice in choices_data:
            if choice.get('choice_type') == ChoiceType.POSITIVE:
                chosen_employee_id = choice.get('chosen_employee_id')
                if chosen_employee_id:
                    popularity_scores[chosen_employee_id] = (
                        popularity_scores.get(chosen_employee_id, 0) + 1
                    )
        return popularity_scores

    @staticmethod
    def calculate_rejection(choices_data: List[Dict]) -> Dict[UUID, int]:
        """Расчет отторжения (отрицательная степень входа).

        Args:
            choices_data: Список словарей с данными выборов

        Returns:
            Словарь {employee_id: количество_отрицательных_выборов}
        """
        rejection_scores = {}
        for choice in choices_data:
            if choice.get('choice_type') == ChoiceType.NEGATIVE:
                chosen_employee_id = choice.get('chosen_employee_id')
                if chosen_employee_id:
                    rejection_scores[chosen_employee_id] = (
                        rejection_scores.get(chosen_employee_id, 0) + 1
                    )
        return rejection_scores

    @staticmethod
    def calculate_expansiveness(choices_data: List[Dict]) -> Dict[UUID, int]:
        """Расчет экспансивности (степень выхода).

        Args:
            choices_data: Список словарей с данными выборов

        Returns:
            Словарь {participant_id: количество_сделанных_выборов}
        """
        expansiveness_scores = {}
        for choice in choices_data:
            participant_id = choice.get('participant_id')
            if participant_id:
                expansiveness_scores[participant_id] = (
                    expansiveness_scores.get(participant_id, 0) + 1
                )
        return expansiveness_scores

    @staticmethod
    def calculate_mutual_choices(choices_data: List[Dict]) -> List[Tuple]:
        """Расчет взаимных выборов.

        Args:
            choices_data: Список словарей с данными выборов

        Returns:
            Список кортежей с парами взаимных выборов
        """
        mutual_pairs = []
        choices_dict = {}

        for choice in choices_data:
            participant_id = choice.get('participant_id')
            chosen_employee_id = choice.get('chosen_employee_id')
            choice_type = choice.get('choice_type')

            if participant_id and chosen_employee_id:
                key = (participant_id, chosen_employee_id)
                choices_dict[key] = choice

                reverse_key = (chosen_employee_id, participant_id)
                if reverse_key in choices_dict:
                    reverse_choice = choices_dict[reverse_key]
                    # Проверяем, что оба выбора положительные
                    if (
                        choice_type == ChoiceType.POSITIVE
                        and reverse_choice.get('choice_type') == ChoiceType.POSITIVE
                    ):
                        mutual_pairs.append((key, reverse_key))

        return mutual_pairs

    @staticmethod
    def calculate_group_cohesion(choices_data: List[Dict], total_participants: int) -> float:
        """Расчет сплоченности группы.

        Args:
            choices_data: Список словарей с данными выборов
            total_participants: Общее количество участников

        Returns:
            Коэффициент сплоченности группы (0.0 - 1.0)
        """
        if total_participants <= 1:
            return 0.0

        total_possible_choices = total_participants * (total_participants - 1)
        actual_positive_choices = len(
            [c for c in choices_data if c.get('choice_type') == ChoiceType.POSITIVE]
        )

        return (
            actual_positive_choices / total_possible_choices if total_possible_choices > 0 else 0.0
        )


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


def generate_recommendations(
    popularity_scores: Dict[UUID, int],
    rejection_scores: Dict[UUID, int],
    stars_and_isolates: Dict[str, List[Dict]],
    group_cohesion: float,
) -> List[str]:
    """Генерация рекомендаций для HR на основе социометрических данных.

    Args:
        popularity_scores: Словарь популярности участников
        rejection_scores: Словарь отторжения участников
        stars_and_isolates: Данные о звездах и изолятах
        group_cohesion: Коэффициент сплоченности группы

    Returns:
        Список рекомендаций
    """
    recommendations = []

    # Анализ изолятов
    if stars_and_isolates.get('isolates'):
        recommendations.append(
            'Выявлены социально изолированные сотрудники. '
            'Рекомендуется провести индивидуальные беседы и '
            'разработать программы интеграции.'
        )

    # Анализ звезд
    if stars_and_isolates.get('stars'):
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
        # Получаем прогресс теста
        # TODO: Получить критерии из БД по cycle_user_id
        # cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)
        # cycle_company = await survey_cycle_for_company_crud.get_or_404(
        #     session, cycle_user.survey_cycle_for_company_id
        # )

        # Здесь должна быть логика получения критериев и ответов
        # Пока возвращаем базовую структуру
        total_criteria = 5  # Заглушка - должно быть получено из БД
        answered_count = 3  # Заглушка - должно быть получено из БД
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
