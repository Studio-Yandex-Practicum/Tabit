# Логика выбора вопросов для социометрического теста

## Обзор

В социометрическом тесте Tabit за одну итерацию отображается 4 вопроса. Данный документ описывает алгоритмы и стратегии выбора вопросов для обеспечения сбалансированного и эффективного тестирования.

**Важно**: Обычные пользователи могут использовать только сбалансированную стратегию выбора вопросов. Изменение стратегии доступно только модераторам компании.

## Стратегии выбора вопросов

### 1. Сбалансированная стратегия (по умолчанию для пользователей)

```python
# src/business_logic/sociometric_question_selector.py

from typing import List, Dict, Optional
from enum import Enum
import random

from src.models.enum import ChoiceTypeEnum
from src.constants.sociometric_criteria import SociometricCategory


class QuestionSelectionStrategy(str, Enum):
    """Стратегии выбора вопросов для социометрии."""
    BALANCED = "balanced"  # Сбалансированная стратегия (единственная для пользователей)
    CATEGORY_FOCUSED = "category_focused"  # Фокус на категории (только для модераторов)
    TYPE_FOCUSED = "type_focused"  # Фокус на типе вопроса (только для модераторов)
    RANDOM = "random"  # Случайный выбор (только для модераторов)
    ADAPTIVE = "adaptive"  # Адаптивный выбор (только для модераторов)


class SociometricQuestionSelector:
    """Класс для выбора вопросов социометрического теста."""

    def __init__(self, strategy: QuestionSelectionStrategy = QuestionSelectionStrategy.BALANCED, is_moderator: bool = False):
        self.strategy = strategy
        self.is_moderator = is_moderator

    async def select_questions(
        self,
        session,
        available_criteria: List[Dict],
        questions_per_iteration: int = 4,
        previous_questions: Optional[List[str]] = None,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """Выбрать вопросы для текущей итерации теста."""

        # Для обычных пользователей всегда используем сбалансированную стратегию
        if not self.is_moderator:
            self.strategy = QuestionSelectionStrategy.BALANCED

        if self.strategy == QuestionSelectionStrategy.BALANCED:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, previous_questions
            )
        elif self.strategy == QuestionSelectionStrategy.CATEGORY_FOCUSED and self.is_moderator:
            return await self._select_category_focused_questions(
                available_criteria, questions_per_iteration, user_preferences
            )
        elif self.strategy == QuestionSelectionStrategy.TYPE_FOCUSED and self.is_moderator:
            return await self._select_type_focused_questions(
                available_criteria, questions_per_iteration, user_preferences
            )
        elif self.strategy == QuestionSelectionStrategy.RANDOM and self.is_moderator:
            return await self._select_random_questions(
                available_criteria, questions_per_iteration
            )
        elif self.strategy == QuestionSelectionStrategy.ADAPTIVE and self.is_moderator:
            return await self._select_adaptive_questions(
                available_criteria, questions_per_iteration, previous_questions, user_preferences
            )
        else:
            # Fallback на сбалансированную стратегию
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, previous_questions
            )

    async def _select_balanced_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        previous_questions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Сбалансированная стратегия выбора вопросов.

        Правила:
        1. 2 вопроса из тактического лидерства
        2. 2 вопроса из стратегического лидерства
        3. Равномерное распределение по типам (POSITIVE, NEGATIVE, NEUTRAL)
        4. Исключение уже заданных вопросов
        """

        # Группируем критерии по категориям
        tactical_criteria = [c for c in available_criteria if c.get('category') == SociometricCategory.TACTICAL_LEADERSHIP]
        strategic_criteria = [c for c in available_criteria if c.get('category') == SociometricCategory.STRATEGIC_LEADERSHIP]

        # Исключаем уже заданные вопросы
        if previous_questions:
            tactical_criteria = [c for c in tactical_criteria if c['criterion_id'] not in previous_questions]
            strategic_criteria = [c for c in strategic_criteria if c['criterion_id'] not in previous_questions]

        selected_questions = []

        # Выбираем 2 вопроса из тактического лидерства
        if len(tactical_criteria) >= 2:
            tactical_selected = self._select_by_type_balance(tactical_criteria, 2)
            selected_questions.extend(tactical_selected)
        else:
            selected_questions.extend(tactical_criteria)

        # Выбираем 2 вопроса из стратегического лидерства
        if len(strategic_criteria) >= 2:
            strategic_selected = self._select_by_type_balance(strategic_criteria, 2)
            selected_questions.extend(strategic_selected)
        else:
            selected_questions.extend(strategic_criteria)

        # Если не хватает вопросов, добавляем из другой категории
        while len(selected_questions) < questions_per_iteration:
            remaining_criteria = [c for c in available_criteria if c not in selected_questions]
            if not remaining_criteria:
                break
            selected_questions.append(random.choice(remaining_criteria))

        return selected_questions[:questions_per_iteration]

    def _select_by_type_balance(
        self,
        criteria: List[Dict],
        count: int
    ) -> List[Dict]:
        """Выбрать критерии с балансом по типам."""

        # Группируем по типам
        positive_criteria = [c for c in criteria if c['choice_type'] == ChoiceTypeEnum.POSITIVE]
        negative_criteria = [c for c in criteria if c['choice_type'] == ChoiceTypeEnum.NEGATIVE]
        neutral_criteria = [c for c in criteria if c['choice_type'] == ChoiceTypeEnum.NEUTRAL]

        selected = []

        # Стараемся выбрать хотя бы один положительный
        if positive_criteria and count > 0:
            selected.append(random.choice(positive_criteria))
            count -= 1

        # Добавляем остальные с учетом баланса
        remaining_criteria = []
        if count > 0:
            remaining_criteria.extend(negative_criteria)
            remaining_criteria.extend(neutral_criteria)

            if remaining_criteria:
                additional = random.sample(remaining_criteria, min(count, len(remaining_criteria)))
                selected.extend(additional)

        return selected

    async def _select_category_focused_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Стратегия с фокусом на категории (только для модераторов).

        Выбирает вопросы преимущественно из одной категории
        на основе предпочтений пользователя или анализа предыдущих ответов.
        """

        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, None
            )

        if user_preferences and 'preferred_category' in user_preferences:
            preferred_category = user_preferences['preferred_category']
            category_criteria = [c for c in available_criteria if c.get('category') == preferred_category]

            if len(category_criteria) >= questions_per_iteration:
                return random.sample(category_criteria, questions_per_iteration)
            else:
                # Добавляем вопросы из другой категории
                other_criteria = [c for c in available_criteria if c.get('category') != preferred_category]
                additional_needed = questions_per_iteration - len(category_criteria)

                selected = category_criteria.copy()
                if other_criteria:
                    additional = random.sample(other_criteria, min(additional_needed, len(other_criteria)))
                    selected.extend(additional)

                return selected

        # Если нет предпочтений, выбираем случайную категорию
        categories = list(set(c.get('category') for c in available_criteria))
        if categories:
            random_category = random.choice(categories)
            category_criteria = [c for c in available_criteria if c.get('category') == random_category]
            return random.sample(category_criteria, min(questions_per_iteration, len(category_criteria)))

        return random.sample(available_criteria, min(questions_per_iteration, len(available_criteria)))

    async def _select_type_focused_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Стратегия с фокусом на типе вопроса (только для модераторов).

        Выбирает вопросы преимущественно одного типа
        (POSITIVE, NEGATIVE, NEUTRAL).
        """

        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, None
            )

        if user_preferences and 'preferred_type' in user_preferences:
            preferred_type = user_preferences['preferred_type']
            type_criteria = [c for c in available_criteria if c['choice_type'] == preferred_type]

            if len(type_criteria) >= questions_per_iteration:
                return random.sample(type_criteria, questions_per_iteration)
            else:
                # Добавляем вопросы других типов
                other_criteria = [c for c in available_criteria if c['choice_type'] != preferred_type]
                additional_needed = questions_per_iteration - len(type_criteria)

                selected = type_criteria.copy()
                if other_criteria:
                    additional = random.sample(other_criteria, min(additional_needed, len(other_criteria)))
                    selected.extend(additional)

                return selected

        # Если нет предпочтений, выбираем случайный тип
        types = list(set(c['choice_type'] for c in available_criteria))
        if types:
            random_type = random.choice(types)
            type_criteria = [c for c in available_criteria if c['choice_type'] == random_type]
            return random.sample(type_criteria, min(questions_per_iteration, len(type_criteria)))

        return random.sample(available_criteria, min(questions_per_iteration, len(available_criteria)))

    async def _select_random_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int
    ) -> List[Dict]:
        """Случайный выбор вопросов (только для модераторов)."""

        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, None
            )

        return random.sample(available_criteria, min(questions_per_iteration, len(available_criteria)))

    async def _select_adaptive_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        previous_questions: Optional[List[str]] = None,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Адаптивная стратегия выбора вопросов (только для модераторов).

        Анализирует предыдущие ответы и адаптирует выбор вопросов
        для получения более точной картины.
        """

        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, previous_questions
            )

        # Анализируем предыдущие ответы
        if previous_questions and user_preferences and 'previous_answers' in user_preferences:
            previous_answers = user_preferences['previous_answers']

            # Анализируем паттерны ответов
            positive_count = sum(1 for answer in previous_answers if answer.get('choice_type') == ChoiceTypeEnum.POSITIVE)
            negative_count = sum(1 for answer in previous_answers if answer.get('choice_type') == ChoiceTypeEnum.NEGATIVE)
            neutral_count = sum(1 for answer in previous_answers if answer.get('choice_type') == ChoiceTypeEnum.NEUTRAL)

            # Определяем недостающие типы вопросов
            total_answers = len(previous_answers)
            if total_answers > 0:
                positive_ratio = positive_count / total_answers
                negative_ratio = negative_count / total_answers
                neutral_ratio = neutral_count / total_answers

                # Выбираем вопросы для балансировки
                selected = []

                # Если мало положительных ответов, добавляем положительные вопросы
                if positive_ratio < 0.3 and questions_per_iteration > 0:
                    positive_criteria = [c for c in available_criteria if c['choice_type'] == ChoiceTypeEnum.POSITIVE]
                    if positive_criteria:
                        selected.append(random.choice(positive_criteria))
                        questions_per_iteration -= 1

                # Если мало отрицательных ответов, добавляем отрицательные вопросы
                if negative_ratio < 0.2 and questions_per_iteration > 0:
                    negative_criteria = [c for c in available_criteria if c['choice_type'] == ChoiceTypeEnum.NEGATIVE]
                    if negative_criteria:
                        selected.append(random.choice(negative_criteria))
                        questions_per_iteration -= 1

                # Заполняем оставшиеся слоты
                remaining_criteria = [c for c in available_criteria if c not in selected]
                if remaining_criteria and questions_per_iteration > 0:
                    additional = random.sample(remaining_criteria, min(questions_per_iteration, len(remaining_criteria)))
                    selected.extend(additional)

                return selected

        # Если нет данных для адаптации, используем сбалансированную стратегию
        return await self._select_balanced_questions(available_criteria, questions_per_iteration, previous_questions)
```

### 2. Конфигурация стратегий

```python
# src/core/config/sociometric.py

from pydantic import BaseModel
from typing import Optional

from src.business_logic.sociometric_question_selector import QuestionSelectionStrategy


class SociometricConfig(BaseModel):
    """Конфигурация социометрического тестирования."""

    # Основные настройки
    questions_per_iteration: int = 4
    default_strategy: QuestionSelectionStrategy = QuestionSelectionStrategy.BALANCED

    # Настройки стратегий
    balanced_strategy: dict = {
        "tactical_questions": 2,
        "strategic_questions": 2,
        "min_positive_ratio": 0.25,
        "min_negative_ratio": 0.15,
        "min_neutral_ratio": 0.25
    }

    category_focused_strategy: dict = {
        "category_weight": 0.7,  # 70% вопросов из предпочтительной категории
        "fallback_weight": 0.3   # 30% вопросов из других категорий
    }

    type_focused_strategy: dict = {
        "type_weight": 0.6,      # 60% вопросов предпочтительного типа
        "fallback_weight": 0.4   # 40% вопросов других типов
    }

    adaptive_strategy: dict = {
        "min_answers_for_adaptation": 4,
        "positive_ratio_threshold": 0.3,
        "negative_ratio_threshold": 0.2,
        "neutral_ratio_threshold": 0.25
    }

    # Настройки прогресса
    max_iterations: int = 7  # Максимум 7 итераций (28 вопросов / 4 вопроса за итерацию)
    min_iterations: int = 3  # Минимум 3 итерации

    # Настройки валидации
    allow_duplicate_questions: bool = False
    require_all_categories: bool = True
    require_all_types: bool = True

    # Настройки для пользователей
    user_min_completion_percentage: float = 100.0  # Обычные пользователи должны ответить на все вопросы
    # Модераторы не проходят тесты - они их создают и управляют
```

### 3. API для получения вопросов

```python
# src/features_v1/company_survey_management/endpoints.py - добавления

@router.get(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/questions',
    dependencies=[Depends(current_user_tabit)],
    summary='Получить вопросы для социометрического теста',
    description='Получить 4 вопроса для текущей итерации социометрического теста. Обычные пользователи используют только сбалансированную стратегию.',
)
async def get_sociometric_questions(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    cycle_user = await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Получаем доступные критерии для компании
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    available_criteria = await sociometric_criterion_crud.get_by_company(session, company.id)

    # Получаем предыдущие вопросы (если есть)
    previous_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
    previous_questions = list(set(choice.criterion_id for choice in previous_choices))

    # Определяем, является ли пользователь модератором
    current_user = await get_current_user(session)
    is_moderator = await check_user_is_moderator(session, current_user.id, company.id)

    # Для обычных пользователей всегда используем сбалансированную стратегию
    strategy = QuestionSelectionStrategy.BALANCED

    # Выбираем вопросы
    selector = SociometricQuestionSelector(strategy, is_moderator=is_moderator)
    selected_questions = await selector.select_questions(
        session=session,
        available_criteria=available_criteria,
        questions_per_iteration=4,
        previous_questions=previous_questions,
        user_preferences=None  # Убираем пользовательские предпочтения
    )

    return {
        "iteration": len(previous_questions) // 4 + 1,
        "total_iterations": len(available_criteria) // 4,
        "strategy": strategy,
        "is_moderator": is_moderator,
        "questions": [
            {
                "criterion_id": question["criterion_id"],
                "name": question["name"],
                "description": question["description"],
                "choice_type": question["choice_type"],
                "max_choices": question["max_choices"],
                "category": question["category"]
            }
            for question in selected_questions
        ]
    }


@router.post(
    '/cycle/{cycle_company_id}/{cycle_user_id}/sociometric/questions/strategy',
    dependencies=[Depends(current_company_moderator)],  # Только для модераторов
    summary='Изменить стратегию выбора вопросов',
    description='Изменить стратегию выбора вопросов для социометрического теста. Доступно только модераторам.',
)
async def change_question_strategy(
    company_slug: str,
    cycle_company_id: int,
    cycle_user_id: int,
    strategy: QuestionSelectionStrategy,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    await company_crud.get_by_slug(session, company_slug, raise_404=True)
    await survey_cycle_for_company_crud.get_or_404(session, cycle_company_id)
    await survey_cycle_for_user_crud.get_or_404(session, cycle_user_id)

    # Сохраняем предпочтение модератора
    await save_moderator_strategy_preference(session, cycle_user_id, strategy)

    return {
        "message": f"Стратегия изменена на {strategy}",
        "strategy": strategy,
        "note": "Изменение стратегии доступно только модераторам"
    }
```

### 4. Логика прогресса теста

```python
# src/business_logic/sociometric_progress.py

from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.crud_surveys import sociometric_choice_crud, sociometric_criterion_crud


class SociometricProgressTracker:
    """Отслеживание прогресса социометрического теста."""

    @staticmethod
    async def get_test_progress(
        session: AsyncSession,
        cycle_user_id: int,
        company_id: int,
        is_moderator: bool = False
    ) -> Dict:
        """Получить прогресс теста."""

        # Получаем все критерии компании
        all_criteria = await sociometric_criterion_crud.get_by_company(session, company_id)
        total_criteria = len(all_criteria)

        # Получаем отвеченные вопросы
        answered_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
        answered_criteria = list(set(choice.criterion_id for choice in answered_choices))
        answered_count = len(answered_criteria)

        # Рассчитываем прогресс
        progress_percentage = (answered_count / total_criteria) * 100 if total_criteria > 0 else 0

        # Определяем текущую итерацию
        current_iteration = (answered_count // 4) + 1
        total_iterations = (total_criteria + 3) // 4  # Округление вверх

        # Определяем статус теста
        if answered_count == 0:
            status = "not_started"
        elif answered_count < total_criteria:
            status = "in_progress"
        else:
            status = "completed"

        return {
            "status": status,
            "progress_percentage": progress_percentage,
            "answered_count": answered_count,
            "total_criteria": total_criteria,
            "current_iteration": current_iteration,
            "total_iterations": total_iterations,
            "remaining_questions": total_criteria - answered_count,
            "next_iteration_questions": min(4, total_criteria - answered_count),
            "is_moderator": is_moderator
        }

    @staticmethod
    async def get_remaining_criteria(
        session: AsyncSession,
        cycle_user_id: int,
        company_id: int
    ) -> List[Dict]:
        """Получить оставшиеся критерии для теста."""

        # Получаем все критерии
        all_criteria = await sociometric_criterion_crud.get_by_company(session, company_id)
        all_criteria_ids = [c.id for c in all_criteria]

        # Получаем отвеченные критерии
        answered_choices = await sociometric_choice_crud.get_by_cycle_user(session, cycle_user_id)
        answered_criteria_ids = list(set(choice.criterion_id for choice in answered_choices))

        # Находим оставшиеся критерии
        remaining_criteria_ids = [cid for cid in all_criteria_ids if cid not in answered_criteria_ids]
        remaining_criteria = [c for c in all_criteria if c.id in remaining_criteria_ids]

        return remaining_criteria

    @staticmethod
    async def can_complete_test(
        session: AsyncSession,
        cycle_user_id: int,
        company_id: int,
        is_moderator: bool = False
    ) -> bool:
        """Проверить, можно ли завершить тест."""

        progress = await SociometricProgressTracker.get_test_progress(
            session, cycle_user_id, company_id, is_moderator
        )

        # Порог завершения теста
        # Модераторы не проходят тесты - они их создают и управляют
        min_percentage = 100.0  # Все пользователи должны ответить на все вопросы

        return progress["progress_percentage"] >= min_percentage
```

## Примеры использования

### 1. Сбалансированная стратегия (по умолчанию для пользователей)

```python
# Пример выбора вопросов для первой итерации
questions = await selector.select_questions(
    available_criteria=all_criteria,
    questions_per_iteration=4,
    previous_questions=[],
    user_preferences=None,
    is_moderator=False  # Обычный пользователь
)

# Результат: 2 вопроса тактического + 2 вопроса стратегического лидерства
# Пример: [T1, T2, S1, S2]
```

### 2. Адаптивная стратегия (только для модераторов)

```python
# Пример адаптивного выбора на основе предыдущих ответов
user_preferences = {
    "previous_answers": [
        {"choice_type": "positive", "criterion_id": "T1"},
        {"choice_type": "positive", "criterion_id": "T2"},
        {"choice_type": "positive", "criterion_id": "S1"},
        {"choice_type": "positive", "criterion_id": "S2"}
    ]
}

questions = await selector.select_questions(
    available_criteria=all_criteria,
    questions_per_iteration=4,
    previous_questions=["T1", "T2", "S1", "S2"],
    user_preferences=user_preferences,
    is_moderator=True  # Только для модераторов
)

# Результат: больше отрицательных и нейтральных вопросов для баланса
# Пример: [T8, T9, S8, T10]
```

### 3. Категорийная стратегия (только для модераторов)

```python
# Пример фокуса на тактическом лидерстве
user_preferences = {
    "preferred_category": "tactical_leadership"
}

questions = await selector.select_questions(
    available_criteria=all_criteria,
    questions_per_iteration=4,
    user_preferences=user_preferences,
    is_moderator=True  # Только для модераторов
)

# Результат: 3 вопроса тактического + 1 вопрос стратегического
# Пример: [T1, T2, T3, S1]
```

## Рекомендации по выбору стратегии

### 1. **Для обычных пользователей**
- **Только BALANCED** стратегия для получения сбалансированной картины
- Нет возможности изменения стратегии
- Должны ответить на все вопросы для завершения теста

### 2. **Для модераторов**
- **BALANCED** - для стандартного тестирования
- **ADAPTIVE** - для уточнения результатов на основе предыдущих ответов
- **CATEGORY_FOCUSED** - для оценки конкретных навыков
- **RANDOM** - для случайной выборки
- Модераторы не проходят тесты - они их создают и управляют

### 3. **Для целевой оценки**
- Используйте **CATEGORY_FOCUSED** для оценки конкретных навыков (только модераторы)

### 4. **Для быстрого тестирования**
- Используйте **RANDOM** стратегию для случайной выборки (только модераторы)

## Безопасность и ограничения

### 1. **Ограничения для обычных пользователей**
- Не могут изменять стратегию выбора вопросов
- Не могут настраивать пользовательские предпочтения
- Должны ответить на все вопросы для завершения теста
- Используют только сбалансированную стратегию

### 2. **Возможности модераторов**
- Могут изменять стратегию выбора вопросов для тестирования
- Могут использовать адаптивные алгоритмы для настройки тестов
- Могут управлять критериями социометрии
- Имеют доступ ко всем стратегиям для настройки тестирования
- Модераторы не проходят тесты - они их создают и управляют

Эта система обеспечивает стандартизацию социометрического тестирования для обычных пользователей, сохраняя при этом гибкость для модераторов! 🎯
