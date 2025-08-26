import random
from typing import Dict, List, Optional

from src.constants.sociometric import QuestionSelectionStrategy
from src.models.enum import ChoiceType, SociometricCategoryEnum


class SociometricQuestionSelector:
    """Класс для выбора вопросов социометрического теста."""

    def __init__(
        self,
        strategy: QuestionSelectionStrategy = QuestionSelectionStrategy.BALANCED,
        is_moderator: bool = False,
    ):
        self.strategy = strategy
        self.is_moderator = is_moderator

        # Принудительно устанавливаем BALANCED для обычных пользователей
        if not self.is_moderator:
            self.strategy = QuestionSelectionStrategy.BALANCED

    async def select_questions(
        self,
        session,
        available_criteria: List,
        questions_per_iteration: int = 4,
        previous_questions: Optional[List[int]] = None,
        user_preferences: Optional[Dict] = None,
    ) -> List[Dict]:
        """Выбрать вопросы для текущей итерации теста."""

        # Для обычных пользователей всегда используем сбалансированную стратегию
        if not self.is_moderator:
            self.strategy = QuestionSelectionStrategy.BALANCED

        # Нормализуем вход (ORM -> dict)
        normalized = [
            {
                'criterion_id': c.id,
                'name': c.name,
                'description': c.description,
                'choice_type': c.choice_type,
                'max_choices': c.max_choices,
                'category': getattr(c, 'category', SociometricCategoryEnum.TACTICAL_LEADERSHIP),
            }
            for c in available_criteria
        ]

        if self.strategy == QuestionSelectionStrategy.BALANCED:
            return await self._select_balanced_questions(
                normalized, questions_per_iteration, previous_questions
            )
        elif self.strategy == QuestionSelectionStrategy.CATEGORY_FOCUSED and self.is_moderator:
            return await self._select_category_focused_questions(
                normalized, questions_per_iteration, user_preferences
            )
        elif self.strategy == QuestionSelectionStrategy.TYPE_FOCUSED and self.is_moderator:
            return await self._select_type_focused_questions(
                normalized, questions_per_iteration, user_preferences
            )
        elif self.strategy == QuestionSelectionStrategy.RANDOM and self.is_moderator:
            return await self._select_random_questions(normalized, questions_per_iteration)
        elif self.strategy == QuestionSelectionStrategy.ADAPTIVE and self.is_moderator:
            return await self._select_adaptive_questions(
                normalized, questions_per_iteration, previous_questions, user_preferences
            )
        else:
            return await self._select_balanced_questions(
                normalized, questions_per_iteration, previous_questions
            )

    async def _select_balanced_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        previous_questions: Optional[List[int]] = None,
    ) -> List[Dict]:
        """
        Сбалансированная стратегия выбора вопросов.
        2 тактических + 2 стратегических; избегаем повторов.
        """

        tactical_criteria = [
            c
            for c in available_criteria
            if c.get('category') == SociometricCategoryEnum.TACTICAL_LEADERSHIP
        ]
        strategic_criteria = [
            c
            for c in available_criteria
            if c.get('category') == SociometricCategoryEnum.STRATEGIC_LEADERSHIP
        ]

        if previous_questions:
            tactical_criteria = [
                c for c in tactical_criteria if c['criterion_id'] not in previous_questions
            ]
            strategic_criteria = [
                c for c in strategic_criteria if c['criterion_id'] not in previous_questions
            ]

        selected: List[Dict] = []

        if len(tactical_criteria) >= 2:
            selected.extend(self._select_by_type_balance(tactical_criteria, 2))
        else:
            selected.extend(tactical_criteria)

        if len(strategic_criteria) >= 2:
            selected.extend(self._select_by_type_balance(strategic_criteria, 2))
        else:
            selected.extend(strategic_criteria)

        while len(selected) < questions_per_iteration:
            remaining = [c for c in available_criteria if c not in selected]
            if not remaining:
                break
            selected.append(random.choice(remaining))

        return selected[:questions_per_iteration]

    def _select_by_type_balance(self, criteria: List[Dict], count: int) -> List[Dict]:
        positive = [c for c in criteria if c['choice_type'] == ChoiceType.POSITIVE]
        negative = [c for c in criteria if c['choice_type'] == ChoiceType.NEGATIVE]
        neutral = [c for c in criteria if c['choice_type'] == ChoiceType.NEUTRAL]

        selected: List[Dict] = []
        if positive and count > 0:
            selected.append(random.choice(positive))
            count -= 1

        remaining: List[Dict] = []
        if count > 0:
            remaining.extend(negative)
            remaining.extend(neutral)
            if remaining:
                selected.extend(random.sample(remaining, min(count, len(remaining))))
        return selected

    async def _select_category_focused_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        user_preferences: Optional[Dict] = None,
    ) -> List[Dict]:
        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, None
            )
        if user_preferences and 'preferred_category' in user_preferences:
            preferred = user_preferences['preferred_category']
            in_cat = [c for c in available_criteria if c.get('category') == preferred]
            if len(in_cat) >= questions_per_iteration:
                return random.sample(in_cat, questions_per_iteration)
            other = [c for c in available_criteria if c.get('category') != preferred]
            selected = in_cat.copy()
            if other:
                selected.extend(
                    random.sample(other, min(questions_per_iteration - len(in_cat), len(other)))
                )
            return selected
        categories = list(set(c.get('category') for c in available_criteria))
        if categories:
            chosen = random.choice(categories)
            in_cat = [c for c in available_criteria if c.get('category') == chosen]
            return random.sample(in_cat, min(questions_per_iteration, len(in_cat)))
        return random.sample(
            available_criteria, min(questions_per_iteration, len(available_criteria))
        )

    async def _select_type_focused_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        user_preferences: Optional[Dict] = None,
    ) -> List[Dict]:
        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, None
            )
        if user_preferences and 'preferred_type' in user_preferences:
            preferred = user_preferences['preferred_type']
            of_type = [c for c in available_criteria if c['choice_type'] == preferred]
            if len(of_type) >= questions_per_iteration:
                return random.sample(of_type, questions_per_iteration)
            other = [c for c in available_criteria if c['choice_type'] != preferred]
            selected = of_type.copy()
            if other:
                selected.extend(
                    random.sample(other, min(questions_per_iteration - len(of_type), len(other)))
                )
            return selected
        types = list(set(c['choice_type'] for c in available_criteria))
        if types:
            chosen = random.choice(types)
            of_type = [c for c in available_criteria if c['choice_type'] == chosen]
            return random.sample(of_type, min(questions_per_iteration, len(of_type)))
        return random.sample(
            available_criteria, min(questions_per_iteration, len(available_criteria))
        )

    async def _select_random_questions(
        self, available_criteria: List[Dict], questions_per_iteration: int
    ) -> List[Dict]:
        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, None
            )
        return random.sample(
            available_criteria, min(questions_per_iteration, len(available_criteria))
        )

    async def _select_adaptive_questions(
        self,
        available_criteria: List[Dict],
        questions_per_iteration: int,
        previous_questions: Optional[List[int]] = None,
        user_preferences: Optional[Dict] = None,
    ) -> List[Dict]:
        if not self.is_moderator:
            return await self._select_balanced_questions(
                available_criteria, questions_per_iteration, previous_questions
            )
        if previous_questions and user_preferences and 'previous_answers' in user_preferences:
            prev = user_preferences['previous_answers']
            positive_count = sum(1 for a in prev if a.get('choice_type') == ChoiceType.POSITIVE)
            negative_count = sum(1 for a in prev if a.get('choice_type') == ChoiceType.NEGATIVE)

            total = len(prev)
            selected: List[Dict] = []
            if total > 0:
                if positive_count / total < 0.3 and questions_per_iteration > 0:
                    pos = [
                        c for c in available_criteria if c['choice_type'] == ChoiceType.POSITIVE
                    ]
                    if pos:
                        selected.append(random.choice(pos))
                        questions_per_iteration -= 1
                if negative_count / total < 0.2 and questions_per_iteration > 0:
                    neg = [
                        c for c in available_criteria if c['choice_type'] == ChoiceType.NEGATIVE
                    ]
                    if neg:
                        selected.append(random.choice(neg))
                        questions_per_iteration -= 1
                remaining = [c for c in available_criteria if c not in selected]
                if remaining and questions_per_iteration > 0:
                    selected.extend(
                        random.sample(remaining, min(questions_per_iteration, len(remaining)))
                    )
                return selected
        return await self._select_balanced_questions(
            available_criteria, questions_per_iteration, previous_questions
        )
