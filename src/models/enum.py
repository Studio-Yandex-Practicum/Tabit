"""Модели для перечислений."""

from enum import IntEnum, StrEnum


class ProblemColor(IntEnum):
    """Варианты значений поля color модели Problem."""

    RED = 1
    ORANGE = 2
    YELLOW = 3
    GREEN = 4
    BLUE = 5
    DARK_BLUE = 6  # Синий.
    VIOLET = 7
    BROWN = 8
    GRAY = 9
    BLACK = 10
    WHITE = 11
    PINK = 12
    BEIGE = 13
    VINOUS = 14
    PURPLE = 15


class ProblemType(StrEnum):
    """Варианты значений поля type модели Problem."""

    # TODO: Нужно уточнить варианты и уже тогда придумывать названия констант.
    # В БД сохранятся названия констант, а не их значения.
    A = 'Взаимодействие в коллективе'
    B = 'Оптимизация бизнес-процессов'
    C = 'Взаимодействие в отделе'
    D = 'Стратегические лидеры'
    E = 'Тактические лидеры'
    F = 'Новые сотрудники'
    G = 'Опытные сотрудники'


class ProblemStatus(StrEnum):
    """Варианты значений поля status модели Problem."""

    NEW = 'Новая'
    IN_PROGRESS = 'В работе'
    SUSPENDED = 'Приостановлена'
    COMPLETED = 'Завершена'


class MeetingStatus(StrEnum):
    """Варианты значений поля status модели Meeting."""

    NEW = 'Новая'
    NOT_HELD = 'Не проведена'
    HELD = 'Проведена'
    SUSPENDED = 'Приостановлена'


class MeetingResultEnum(StrEnum):
    """Варианты значений поля result модели MeetingResult."""

    EXCELLENT = 'Отлично'
    GOOD = 'Хорошо'
    BADLY = 'Плохо'
    DISGUSTING = 'Отвратительно'


class TaskStatus(StrEnum):
    """Варианты значений поля status модели Task."""

    NEW = 'Новая'
    IN_PROGRESS = 'В работе'
    NOT_ACCEPTED = 'Не принята'
    COMPLETED = 'Завершена'


class CompanyUserRole(StrEnum):
    """Варианты значений поля role модели CompanyUser."""

    MODERATOR = 'Модератор'
    EMPLOYEE = 'Сотрудник'


class MeetingResultEngagementEnum(StrEnum):
    """Варианты значений поля participant_engagement модели MeetingResult."""

    YES = 'Да'
    MORE_THAN_HALF = 'Больше половины'
    LESS_THAN_HALF = 'Меньше половины'
    NOBODY = 'Никто'


class MeetingResultSolutionEnum(StrEnum):
    """Варианты значений поля meeting_feedback модели MeetingResult."""

    YES = 'Да'
    MORE_YES = 'Скорее да, чем нет'
    MORE_NO = 'Скорее нет, чем да'
    NO = 'Нет'


class SurveysStatus(StrEnum):
    """Варианты значений для статуса тестирований в админ панели."""

    IN_PROGRESS = 'В работе'
    COMPLETED = 'Завершен'
    CANCELED = 'Отменен'
    POSTPONED = 'Отложен'


class LuscherWeightsColorEnum(IntEnum):
    """Веса цветов теста Люшера."""

    Blue = 1
    Green = 2
    Red = 3
    Yellow = 4
    Violet = 5
    Brown = 6
    Black = 7
    Grey = 0


class LuschersColorEnum(StrEnum):
    """Цветов теста Люшера."""

    Blue = 'blue'
    Green = 'green'
    Red = 'red'
    Yellow = 'yellow'
    Violet = 'violet'
    Brown = 'brown'
    Black = 'black'
    Grey = 'grey'
