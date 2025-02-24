from enum import IntEnum, StrEnum


class ColorProblem(IntEnum):
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


class TypeProblem(StrEnum):
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


class StatusProblem(StrEnum):
    """Варианты значений поля status модели Problem."""

    NEW = 'Новая'
    IN_PROGRESS = 'В работе'
    SUSPENDED = 'Приостановлена'
    COMPLETED = 'Завершена'


class StatusMeeting(StrEnum):
    """Варианты значений поля status модели Meeting."""

    NEW = 'Новая'
    NOT_HELD = 'Не проведена'
    HELD = 'Проведена'
    SUSPENDED = 'Приостановлена'


class ResultMeetingEnum(StrEnum):
    """Варианты значений поля result модели ResultMeeting."""

    EXCELLENT = 'Отлично'
    GOOD = 'Хорошо'
    BADLY = 'Плохо'
    DISGUSTING = 'Отвратительно'


class StatusTask(StrEnum):
    """Варианты значений поля status модели Task."""

    NEW = 'Новая'
    IN_PROGRESS = 'В работе'
    NOT_ACCEPTED = 'Не принята'
    COMPLETED = 'Завершена'


class RoleUserTabit(StrEnum):
    """Варианты значений поля role модели UserTabit."""

    ADMIN = 'Админ'
    EMPLOYEE = 'Сотрудник'
