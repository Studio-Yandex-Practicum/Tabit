"""Конфигурация социометрического тестирования."""

from enum import Enum

from pydantic import BaseModel


class QuestionSelectionStrategy(str, Enum):
    """Стратегии выбора вопросов для социометрии."""

    BALANCED = 'balanced'  # Сбалансированная стратегия (единственная для пользователей)
    CATEGORY_FOCUSED = 'category_focused'  # Фокус на категории (только для модераторов)
    TYPE_FOCUSED = 'type_focused'  # Фокус на типе вопроса (только для модераторов)
    RANDOM = 'random'  # Случайный выбор (только для модераторов)
    ADAPTIVE = 'adaptive'  # Адаптивный выбор (только для модераторов)


class SociometricConfig(BaseModel):
    """Конфигурация социометрического тестирования."""

    # Основные настройки
    questions_per_iteration: int = 4
    default_strategy: QuestionSelectionStrategy = QuestionSelectionStrategy.BALANCED

    # Настройки стратегий
    balanced_strategy: dict = {
        'tactical_questions': 2,
        'strategic_questions': 2,
        'min_positive_ratio': 0.25,
        'min_negative_ratio': 0.15,
        'min_neutral_ratio': 0.25,
    }

    category_focused_strategy: dict = {
        'category_weight': 0.7,  # 70% вопросов из предпочтительной категории
        'fallback_weight': 0.3,  # 30% вопросов из других категорий
    }

    type_focused_strategy: dict = {
        'type_weight': 0.6,  # 60% вопросов предпочтительного типа
        'fallback_weight': 0.4,  # 40% вопросов других типов
    }

    adaptive_strategy: dict = {
        'min_answers_for_adaptation': 4,
        'positive_ratio_threshold': 0.3,
        'negative_ratio_threshold': 0.2,
        'neutral_ratio_threshold': 0.25,
    }

    # Настройки прогресса
    max_iterations: int = 7  # Максимум 7 итераций (28 вопросов / 4 вопроса за итерацию)
    min_iterations: int = 3  # Минимум 3 итерации

    # Настройки валидации
    allow_duplicate_questions: bool = False
    require_all_categories: bool = True
    require_all_types: bool = True

    # Настройки для пользователей
    user_min_completion_percentage: float = (
        100.0  # Обычные пользователи должны ответить на все вопросы
    )
    # Модераторы не проходят тесты - они их создают и управляют


class SociometricSecurityConfig(BaseModel):
    """Конфигурация безопасности социометрии."""

    # Ограничения для обычных пользователей
    USER_STRATEGY_RESTRICTION: bool = True  # Только BALANCED стратегия
    USER_PREFERENCE_DISABLED: bool = True  # Отключить пользовательские предпочтения
    USER_MIN_COMPLETION: float = 100.0  # Обычные пользователи должны ответить на все вопросы
    USER_ADAPTIVE_DISABLED: bool = True  # Отключить адаптивные алгоритмы

    # Возможности модераторов
    MODERATOR_ALL_STRATEGIES: bool = True  # Все стратегии доступны для настройки тестов
    MODERATOR_ADAPTIVE_ENABLED: bool = True  # Адаптивные алгоритмы включены для настройки
    # Модераторы не проходят тесты - они их создают и управляют
