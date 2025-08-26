"""Константы критериев социометрии для Tabit."""

from enum import Enum
from typing import Dict, List

from src.models.enum import ChoiceType


class SociometricCategory(str, Enum):
    """Категории социометрических критериев."""

    TACTICAL_LEADERSHIP = 'tactical_leadership'
    STRATEGIC_LEADERSHIP = 'strategic_leadership'


class SociometricCriterionType(str, Enum):
    """Типы социометрических критериев."""

    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'


# Готовые критерии социометрии
SOCIOMETRIC_CRITERIA = {
    SociometricCategory.TACTICAL_LEADERSHIP: {
        'positive': {
            'project_details': {
                'name': 'Детали проекта',
                'description': 'К кому из коллег вы пойдете узнать детали проекта?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 3,
            },
            'procedures_expert': {
                'name': 'Эксперт по процедурам',
                'description': (
                    'Кто в компании чаще всего описывает процедуры, поднимает старые приказы?'
                ),
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'detail_oriented': {
                'name': 'Внимание к деталям',
                'description': 'Кто всегда видит детали проекта и готов копаться в мелочах?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'procedure_follower': {
                'name': 'Следование процедурам',
                'description': 'Кто всегда следует процедуре действий?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'process_coordinator': {
                'name': 'Координатор процессов',
                'description': (
                    'Кто готов взять на себя роль координатора процесса '
                    '(пригласить на встречу, забронировать переговорную комнату и др.)?'
                ),
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'crisis_worker': {
                'name': 'Работа в кризис',
                'description': (
                    'Кто из сотрудников готов работать даже в самый сложный период '
                    'для компании (страны)?'
                ),
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'project_completer': {
                'name': 'Завершение проектов',
                'description': 'Кто может сопроводить проект и доводит его до конца?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
        },
        'negative': {
            'no_training': {
                'name': 'Отказ от обучения',
                'description': 'Кто не тратит время на обучение новых сотрудников?',
                'choice_type': ChoiceType.NEGATIVE,
                'max_choices': 2,
            },
            'over_detail': {
                'name': 'Излишняя детализация',
                'description': 'Кто по вашему мнению излишне закапывается в деталях проекта?',
                'choice_type': ChoiceType.NEGATIVE,
                'max_choices': 2,
            },
        },
        'neutral': {
            'interesting_projects': {
                'name': 'Интересные проекты',
                'description': 'Кто по вашему мнению интереснее всего выполняет свои проекты?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'thorough_planner': {
                'name': 'Тщательное планирование',
                'description': (
                    'Кто по вашему мнению продумывает в работе все до последней мелочи?'
                ),
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'project_savior': {
                'name': 'Спаситель проектов',
                'description': 'Кто подхватывает проект, когда что-то не получается?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'procedure_monitor': {
                'name': 'Мониторинг процедур',
                'description': 'Кто чаще других смотрит за соблюдением правил и процедур?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'idea_rejector': {
                'name': 'Отклонение идей',
                'description': "Кто чаще всего говорит 'нет', когда слышит о новой идее?",
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
        },
    },
    SociometricCategory.STRATEGIC_LEADERSHIP: {
        'positive': {
            'innovation_seeker': {
                'name': 'Поиск инноваций',
                'description': 'Кому в компании важно использовать все новое?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'meeting_speaker': {
                'name': 'Выступления на совещаниях',
                'description': 'Кому критически важно высказываться на совещаниях?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'creative_thinker': {
                'name': 'Творческое мышление',
                'description': (
                    'Кто больше всех считает себя творческой личностью и часто '
                    'генерирует новые идеи?'
                ),
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'future_thinker': {
                'name': 'Долгосрочное планирование',
                'description': 'Кто в компании обычно смотрит на несколько лет вперед?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'risk_taker': {
                'name': 'Принятие рисков',
                'description': 'Кто из сотрудников доводит до конца рискованные идеи?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'tech_innovator': {
                'name': 'Технологические инновации',
                'description': 'Кто из сотрудников чаще высказывается о прорывных технологиях?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
            'conversation_supporter': {
                'name': 'Поддержка в беседах',
                'description': 'Кто из сотрудников чаще может оказать поддержку в беседе?',
                'choice_type': ChoiceType.POSITIVE,
                'max_choices': 2,
            },
        },
        'negative': {
            'incomplete_ideas': {
                'name': 'Незавершенные идеи',
                'description': 'Кто чаще не доводит начатые идеи до конца?',
                'choice_type': ChoiceType.NEGATIVE,
                'max_choices': 2,
            }
        },
        'neutral': {
            'new_project_leader': {
                'name': 'Лидер новых проектов',
                'description': 'Кто чаще всего возглавляет новые проекты?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'risky_idea_generator': {
                'name': 'Генератор рискованных идей',
                'description': 'Кто чаще всего высказывает рискованные идеи?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'idea_generator': {
                'name': 'Генератор идей',
                'description': 'Кто чаще всего генерирует новые идеи?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'responsibility_taker': {
                'name': 'Принятие ответственности',
                'description': 'Кто чаще всего готов взять на себя ответственность за других?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'conflict_resolver': {
                'name': 'Разрешение конфликтов',
                'description': (
                    'Кто чаще всех успокаивает коллег во время разговора и умело '
                    "'сглаживает' углы?"
                ),
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
            'informal_conversation': {
                'name': 'Неформальное общение',
                'description': 'С кем бы вы пошли поговорить на неформальную тему?',
                'choice_type': ChoiceType.NEUTRAL,
                'max_choices': 2,
            },
        },
    },
}


def get_all_criteria() -> Dict[str, Dict]:
    """Получить все критерии в плоском виде."""
    all_criteria = {}

    for category, types in SOCIOMETRIC_CRITERIA.items():
        for choice_type, criteria in types.items():
            for criterion_id, criterion_data in criteria.items():
                all_criteria[criterion_id] = {
                    **criterion_data,
                    'category': category,
                    'criterion_id': criterion_id,
                }

    return all_criteria


def get_criteria_by_category(category: SociometricCategory) -> Dict[str, Dict]:
    """Получить критерии по категории."""
    return SOCIOMETRIC_CRITERIA.get(category, {})


def get_criteria_by_type(choice_type: ChoiceType) -> List[Dict]:
    """Получить критерии по типу выбора."""
    criteria_list = []

    for category, types in SOCIOMETRIC_CRITERIA.items():
        if choice_type.value in types:
            for criterion_id, criterion_data in types[choice_type.value].items():
                criteria_list.append(
                    {**criterion_data, 'category': category, 'criterion_id': criterion_id}
                )

    return criteria_list
