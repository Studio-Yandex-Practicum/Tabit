from datetime import date

from src.schemas.constants import TextError


def validate_not_empty(value: str) -> str:
    """Валидирует название встречи.

    Назначение:
        Валидирует, что строка:
        1. Не является пустой
        2. Не состоит только из пробелов
    Параметры:
        value: Значение для валидации.
    Возвращаемое значение:
        Проверенное значение.
    Исключения:
        ValueError: Если значение пустое или состоит только из пробелов.
    """
    if not value.strip():
        raise ValueError(TextError.MEETING_TITLE_EMPTY)
    return value.strip()


def validate_date(value: date) -> date:
    """Валидирует дату встречи.

    Назначение:
        Валидирует, что строка:
        1. Не находится в прошлом
    Параметры:
        value: Дата для валидации.
    Возвращает:
        Проверенная дата.
    Исключения:
        ValueError: Если дата в прошлом.
    """
    if value < date.today():
        raise ValueError(f'{TextError.DATE_CANNOT_BE_EARLIER} {date.today()}')
    return value
