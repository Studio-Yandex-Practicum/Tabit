# Критерии социометрии для Tabit

## Обзор

Данный документ содержит готовые критерии социометрии для системы Tabit, основанные на практических вопросах для оценки тактического и стратегического лидерства в организациях.

## Структура критериев

### 1. Тактическое лидерство (Tactical Leadership)

#### 1.1 Положительные критерии (POSITIVE)

| ID | Критерий | Описание |
|----|----------|----------|
| T1 | `project_details` | К кому из коллег вы пойдете узнать детали проекта? |
| T2 | `procedures_expert` | Кто в компании чаще всего описывает процедуры, поднимает старые приказы? |
| T3 | `detail_oriented` | Кто всегда видит детали проекта и готов копаться в мелочах? |
| T4 | `procedure_follower` | Кто всегда следует процедуре действий? |
| T5 | `process_coordinator` | Кто готов взять на себя роль координатора процесса (пригласить на встречу, забронировать переговорную комнату и др.)? |
| T6 | `crisis_worker` | Кто из сотрудников готов работать даже в самый сложный период для компании (страны)? |
| T7 | `project_completer` | Кто может сопроводить проект и доводит его до конца? |

#### 1.2 Отрицательные критерии (NEGATIVE)

| ID | Критерий | Описание |
|----|----------|----------|
| T8 | `no_training` | Кто не тратит время на обучение новых сотрудников? |
| T9 | `over_detail` | Кто по вашему мнению излишне закапывается в деталях проекта? |

#### 1.3 Нейтральные критерии (NEUTRAL)

| ID | Критерий | Описание |
|----|----------|----------|
| T10 | `interesting_projects` | Кто по вашему мнению интереснее всего выполняет свои проекты? |
| T11 | `thorough_planner` | Кто по вашему мнению продумывает в работе все до последней мелочи? |
| T12 | `project_savior` | Кто подхватывает проект, когда что-то не получается? |
| T13 | `procedure_monitor` | Кто чаще других смотрит за соблюдением правил и процедур? |
| T14 | `idea_rejector` | Кто чаще всего говорит "нет", когда слышит о новой идее? |

### 2. Стратегическое лидерство (Strategic Leadership)

#### 2.1 Положительные критерии (POSITIVE)

| ID | Критерий | Описание |
|----|----------|----------|
| S1 | `innovation_seeker` | Кому в компании важно использовать все новое? |
| S2 | `meeting_speaker` | Кому критически важно высказываться на совещаниях? |
| S3 | `creative_thinker` | Кто больше всех считает себя творческой личностью и часто генерирует новые идеи? |
| S4 | `future_thinker` | Кто в компании обычно смотрит на несколько лет вперед? |
| S5 | `risk_taker` | Кто из сотрудников доводит до конца рискованные идеи? |
| S6 | `tech_innovator` | Кто из сотрудников чаще высказывается о прорывных технологиях? |
| S7 | `conversation_supporter` | Кто из сотрудников чаще может оказать поддержку в беседе? |

#### 2.2 Отрицательные критерии (NEGATIVE)

| ID | Критерий | Описание |
|----|----------|----------|
| S8 | `incomplete_ideas` | Кто чаще не доводит начатые идеи до конца? |

#### 2.3 Нейтральные критерии (NEUTRAL)

| ID | Критерий | Описание |
|----|----------|----------|
| S9 | `new_project_leader` | Кто чаще всего возглавляет новые проекты? |
| S10 | `risky_idea_generator` | Кто чаще всего высказывает рискованные идеи? |
| S11 | `idea_generator` | Кто чаще всего генерирует новые идеи? |
| S12 | `responsibility_taker` | Кто чаще всего готов взять на себя ответственность за других? |
| S13 | `conflict_resolver` | Кто чаще всех успокаивает коллег во время разговора и умело "сглаживает" углы? |
| S14 | `informal_conversation` | С кем бы вы пошли поговорить на неформальную тему? |

## Реализация в коде

### 1. Константы критериев

```python
# src/constants/sociometric_criteria.py

from enum import Enum
from typing import Dict, List

from src.models.enum import ChoiceTypeEnum


class SociometricCategory(str, Enum):
    """Категории социометрических критериев."""
    TACTICAL_LEADERSHIP = "tactical_leadership"
    STRATEGIC_LEADERSHIP = "strategic_leadership"


class SociometricCriterionType(str, Enum):
    """Типы социометрических критериев."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# Готовые критерии социометрии
SOCIOMETRIC_CRITERIA = {
    SociometricCategory.TACTICAL_LEADERSHIP: {
        "positive": {
            "project_details": {
                "name": "Детали проекта",
                "description": "К кому из коллег вы пойдете узнать детали проекта?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 3
            },
            "procedures_expert": {
                "name": "Эксперт по процедурам",
                "description": "Кто в компании чаще всего описывает процедуры, поднимает старые приказы?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "detail_oriented": {
                "name": "Внимание к деталям",
                "description": "Кто всегда видит детали проекта и готов копаться в мелочах?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "procedure_follower": {
                "name": "Следование процедурам",
                "description": "Кто всегда следует процедуре действий?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "process_coordinator": {
                "name": "Координатор процессов",
                "description": "Кто готов взять на себя роль координатора процесса (пригласить на встречу, забронировать переговорную комнату и др.)?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "crisis_worker": {
                "name": "Работа в кризис",
                "description": "Кто из сотрудников готов работать даже в самый сложный период для компании (страны)?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "project_completer": {
                "name": "Завершение проектов",
                "description": "Кто может сопроводить проект и доводит его до конца?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            }
        },
        "negative": {
            "no_training": {
                "name": "Отказ от обучения",
                "description": "Кто не тратит время на обучение новых сотрудников?",
                "choice_type": ChoiceTypeEnum.NEGATIVE,
                "max_choices": 2
            },
            "over_detail": {
                "name": "Излишняя детализация",
                "description": "Кто по вашему мнению излишне закапывается в деталях проекта?",
                "choice_type": ChoiceTypeEnum.NEGATIVE,
                "max_choices": 2
            }
        },
        "neutral": {
            "interesting_projects": {
                "name": "Интересные проекты",
                "description": "Кто по вашему мнению интереснее всего выполняет свои проекты?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "thorough_planner": {
                "name": "Тщательное планирование",
                "description": "Кто по вашему мнению продумывает в работе все до последней мелочи?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "project_savior": {
                "name": "Спаситель проектов",
                "description": "Кто подхватывает проект, когда что-то не получается?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "procedure_monitor": {
                "name": "Мониторинг процедур",
                "description": "Кто чаще других смотрит за соблюдением правил и процедур?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "idea_rejector": {
                "name": "Отклонение идей",
                "description": "Кто чаще всего говорит 'нет', когда слышит о новой идее?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            }
        }
    },
    SociometricCategory.STRATEGIC_LEADERSHIP: {
        "positive": {
            "innovation_seeker": {
                "name": "Поиск инноваций",
                "description": "Кому в компании важно использовать все новое?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "meeting_speaker": {
                "name": "Выступления на совещаниях",
                "description": "Кому критически важно высказываться на совещаниях?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "creative_thinker": {
                "name": "Творческое мышление",
                "description": "Кто больше всех считает себя творческой личностью и часто генерирует новые идеи?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "future_thinker": {
                "name": "Долгосрочное планирование",
                "description": "Кто в компании обычно смотрит на несколько лет вперед?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "risk_taker": {
                "name": "Принятие рисков",
                "description": "Кто из сотрудников доводит до конца рискованные идеи?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "tech_innovator": {
                "name": "Технологические инновации",
                "description": "Кто из сотрудников чаще высказывается о прорывных технологиях?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            },
            "conversation_supporter": {
                "name": "Поддержка в беседах",
                "description": "Кто из сотрудников чаще может оказать поддержку в беседе?",
                "choice_type": ChoiceTypeEnum.POSITIVE,
                "max_choices": 2
            }
        },
        "negative": {
            "incomplete_ideas": {
                "name": "Незавершенные идеи",
                "description": "Кто чаще не доводит начатые идеи до конца?",
                "choice_type": ChoiceTypeEnum.NEGATIVE,
                "max_choices": 2
            }
        },
        "neutral": {
            "new_project_leader": {
                "name": "Лидер новых проектов",
                "description": "Кто чаще всего возглавляет новые проекты?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "risky_idea_generator": {
                "name": "Генератор рискованных идей",
                "description": "Кто чаще всего высказывает рискованные идеи?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "idea_generator": {
                "name": "Генератор идей",
                "description": "Кто чаще всего генерирует новые идеи?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "responsibility_taker": {
                "name": "Принятие ответственности",
                "description": "Кто чаще всего готов взять на себя ответственность за других?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "conflict_resolver": {
                "name": "Разрешение конфликтов",
                "description": "Кто чаще всех успокаивает коллег во время разговора и умело 'сглаживает' углы?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            },
            "informal_conversation": {
                "name": "Неформальное общение",
                "description": "С кем бы вы пошли поговорить на неформальную тему?",
                "choice_type": ChoiceTypeEnum.NEUTRAL,
                "max_choices": 2
            }
        }
    }
}


def get_all_criteria() -> Dict[str, Dict]:
    """Получить все критерии в плоском виде."""
    all_criteria = {}

    for category, types in SOCIOMETRIC_CRITERIA.items():
        for choice_type, criteria in types.items():
            for criterion_id, criterion_data in criteria.items():
                all_criteria[criterion_id] = {
                    **criterion_data,
                    "category": category,
                    "criterion_id": criterion_id
                }

    return all_criteria


def get_criteria_by_category(category: SociometricCategory) -> Dict[str, Dict]:
    """Получить критерии по категории."""
    return SOCIOMETRIC_CRITERIA.get(category, {})


def get_criteria_by_type(choice_type: ChoiceTypeEnum) -> List[Dict]:
    """Получить критерии по типу выбора."""
    criteria_list = []

    for category, types in SOCIOMETRIC_CRITERIA.items():
        if choice_type.value in types:
            for criterion_id, criterion_data in types[choice_type.value].items():
                criteria_list.append({
                    **criterion_data,
                    "category": category,
                    "criterion_id": criterion_id
                })

    return criteria_list
```

### 2. Фабрика для создания критериев

```python
# src/services/sociometric_criteria_factory.py

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.constants.sociometric_criteria import get_all_criteria, SociometricCategory
from src.crud.crud_surveys import sociometric_criterion_crud
from src.schemas.sociometric import SociometricCriterionCreateSchema


class SociometricCriteriaFactory:
    """Фабрика для создания стандартных критериев социометрии."""

    @staticmethod
    async def create_default_criteria_for_company(
        session: AsyncSession,
        company_id: int
    ) -> List[int]:
        """Создать стандартные критерии для компании."""
        all_criteria = get_all_criteria()
        created_criteria_ids = []

        for criterion_id, criterion_data in all_criteria.items():
            criterion_schema = SociometricCriterionCreateSchema(
                name=criterion_data["name"],
                description=criterion_data["description"],
                choice_type=criterion_data["choice_type"],
                max_choices=criterion_data["max_choices"]
            )

            criterion_db = await sociometric_criterion_crud.create_criterion(
                session, criterion_schema, company_id
            )
            created_criteria_ids.append(criterion_db.id)

        return created_criteria_ids

    @staticmethod
    async def create_tactical_criteria_for_company(
        session: AsyncSession,
        company_id: int
    ) -> List[int]:
        """Создать только критерии тактического лидерства."""
        tactical_criteria = get_criteria_by_category(SociometricCategory.TACTICAL_LEADERSHIP)
        created_criteria_ids = []

        for choice_type, criteria in tactical_criteria.items():
            for criterion_id, criterion_data in criteria.items():
                criterion_schema = SociometricCriterionCreateSchema(
                    name=criterion_data["name"],
                    description=criterion_data["description"],
                    choice_type=criterion_data["choice_type"],
                    max_choices=criterion_data["max_choices"]
                )

                criterion_db = await sociometric_criterion_crud.create_criterion(
                    session, criterion_schema, company_id
                )
                created_criteria_ids.append(criterion_db.id)

        return created_criteria_ids

    @staticmethod
    async def create_strategic_criteria_for_company(
        session: AsyncSession,
        company_id: int
    ) -> List[int]:
        """Создать только критерии стратегического лидерства."""
        strategic_criteria = get_criteria_by_category(SociometricCategory.STRATEGIC_LEADERSHIP)
        created_criteria_ids = []

        for choice_type, criteria in strategic_criteria.items():
            for criterion_id, criterion_data in criteria.items():
                criterion_schema = SociometricCriterionCreateSchema(
                    name=criterion_data["name"],
                    description=criterion_data["description"],
                    choice_type=criterion_data["choice_type"],
                    max_choices=criterion_data["max_choices"]
                )

                criterion_db = await sociometric_criterion_crud.create_criterion(
                    session, criterion_schema, company_id
                )
                created_criteria_ids.append(criterion_db.id)

        return created_criteria_ids
```

### 3. API эндпоинты для управления критериями

```python
# src/features_v1/company_survey_management/endpoints.py - добавления

@router.post(
    '/sociometric/criteria/default',
    dependencies=[Depends(current_company_moderator)],
    summary='Создать стандартные критерии социометрии',
    description='Создать полный набор стандартных критериев социометрии для компании. Доступно только модераторам.',
    status_code=status.HTTP_201_CREATED,
)
async def create_default_sociometric_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    criteria_ids = await SociometricCriteriaFactory.create_default_criteria_for_company(
        session, company.id
    )

    return {
        "message": "Стандартные критерии социометрии созданы",
        "created_criteria_count": len(criteria_ids),
        "criteria_ids": criteria_ids
    }


@router.post(
    '/sociometric/criteria/tactical',
    dependencies=[Depends(current_company_moderator)],
    summary='Создать критерии тактического лидерства',
    description='Создать критерии тактического лидерства для компании. Доступно только модераторам.',
    status_code=status.HTTP_201_CREATED,
)
async def create_tactical_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    criteria_ids = await SociometricCriteriaFactory.create_tactical_criteria_for_company(
        session, company.id
    )

    return {
        "message": "Критерии тактического лидерства созданы",
        "created_criteria_count": len(criteria_ids),
        "criteria_ids": criteria_ids
    }


@router.post(
    '/sociometric/criteria/strategic',
    dependencies=[Depends(current_company_moderator)],
    summary='Создать критерии стратегического лидерства',
    description='Создать критерии стратегического лидерства для компании. Доступно только модераторам.',
    status_code=status.HTTP_201_CREATED,
)
async def create_strategic_criteria(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    criteria_ids = await SociometricCriteriaFactory.create_strategic_criteria_for_company(
        session, company.id
    )

    return {
        "message": "Критерии стратегического лидерства созданы",
        "created_criteria_count": len(criteria_ids),
        "criteria_ids": criteria_ids
    }
```

## Интерпретация результатов

### 1. Анализ тактического лидерства

```python
def analyze_tactical_leadership(sociometric_data: dict) -> dict:
    """Анализ тактического лидерства на основе социометрических данных."""

    tactical_scores = {}

    # Положительные критерии тактического лидерства
    positive_tactical = [
        'project_details', 'procedures_expert', 'detail_oriented',
        'procedure_follower', 'process_coordinator', 'crisis_worker',
        'project_completer'
    ]

    # Отрицательные критерии тактического лидерства
    negative_tactical = ['no_training', 'over_detail']

    for employee_id in sociometric_data['participants']:
        positive_score = sum([
            sociometric_data['individual_scores']['popularity'].get(employee_id, 0)
            for criterion in positive_tactical
            if criterion in sociometric_data['criteria_scores']
        ])

        negative_score = sum([
            sociometric_data['individual_scores']['rejection'].get(employee_id, 0)
            for criterion in negative_tactical
            if criterion in sociometric_data['criteria_scores']
        ])

        tactical_scores[employee_id] = {
            'positive_score': positive_score,
            'negative_score': negative_score,
            'net_score': positive_score - negative_score,
            'leadership_potential': 'high' if positive_score > negative_score else 'low'
        }

    return tactical_scores
```

### 2. Анализ стратегического лидерства

```python
def analyze_strategic_leadership(sociometric_data: dict) -> dict:
    """Анализ стратегического лидерства на основе социометрических данных."""

    strategic_scores = {}

    # Положительные критерии стратегического лидерства
    positive_strategic = [
        'innovation_seeker', 'meeting_speaker', 'creative_thinker',
        'future_thinker', 'risk_taker', 'tech_innovator',
        'conversation_supporter'
    ]

    # Отрицательные критерии стратегического лидерства
    negative_strategic = ['incomplete_ideas']

    for employee_id in sociometric_data['participants']:
        positive_score = sum([
            sociometric_data['individual_scores']['popularity'].get(employee_id, 0)
            for criterion in positive_strategic
            if criterion in sociometric_data['criteria_scores']
        ])

        negative_score = sum([
            sociometric_data['individual_scores']['rejection'].get(employee_id, 0)
            for criterion in negative_strategic
            if criterion in sociometric_data['criteria_scores']
        ])

        strategic_scores[employee_id] = {
            'positive_score': positive_score,
            'negative_score': negative_score,
            'net_score': positive_score - negative_score,
            'leadership_potential': 'high' if positive_score > negative_score else 'low'
        }

    return strategic_scores
```

## Безопасность и ограничения

### 1. Ограничения для обычных пользователей

При использовании социометрических критериев в Tabit действуют следующие ограничения:

1. **Стратегия выбора вопросов**: Обычные пользователи могут использовать только сбалансированную стратегию
2. **Изменение критериев**: Недоступно для обычных пользователей
3. **Настройка параметров**: Отключена
4. **Минимальный порог завершения**: 100% вопросов должны быть отвечены (все вопросы)

### 2. Возможности модераторов

Модераторы компании имеют полный доступ к настройке критериев:

1. **Все стратегии**: Доступны все типы стратегий выбора вопросов для настройки тестов
2. **Управление критериями**: Могут создавать, редактировать и удалять критерии
3. **Настройка параметров**: Могут изменять максимальное количество выборов
4. **Модераторы не проходят тесты**: Они их создают и управляют

## Рекомендации по использованию

### 1. Последовательность проведения

1. **Тактическое лидерство** - оценить способность к операционному управлению
2. **Стратегическое лидерство** - оценить способность к долгосрочному планированию
3. **Комбинированный анализ** - выявить баланс тактических и стратегических навыков

### 2. Интерпретация результатов

- **Высокий тактический + низкий стратегический** = Операционный менеджер
- **Низкий тактический + высокий стратегический** = Стратегический планировщик
- **Высокий тактический + высокий стратегический** = Потенциальный топ-менеджер
- **Низкий тактический + низкий стратегический** = Требует развития лидерских навыков

### 3. Практическое применение

- **Формирование команд** - подбор сотрудников с комплементарными навыками
- **Развитие лидерства** - целевое обучение недостающим навыкам
- **Карьерное планирование** - определение подходящих ролей
- **Управление проектами** - назначение лидеров в зависимости от типа проекта
