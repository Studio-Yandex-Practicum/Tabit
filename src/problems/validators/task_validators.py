from datetime import date
from typing import List
from uuid import UUID

from src.problems.constants import (
    ERROR_DATE_SHOULD_BE_FUTURE,
    ERROR_EXECUTORS_MUST_BE_UUID_FORMAT,
    ERROR_TASK_NAME_EMPTY,
)


def validate_date_in_future(value: date) -> date:
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
    if value is None:
        return None
    if value < date.today():
        raise ValueError(f'{ERROR_DATE_SHOULD_BE_FUTURE} {date.today()}')
    return value


def validate_name(value: str) -> str:
    """Валидирует название задачи.

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
    if value is None:
        return None
    if not value.strip():
        raise ValueError(ERROR_TASK_NAME_EMPTY)
    return value.strip()


def validate_executors(value: List[UUID]) -> List[UUID]:
    """Валидирует список исполнителей.

    Назначение:
        Валидирует, что список:
        1. Не пустой (если передан)
        2. Содержит элементы типа UUID
    Параметры:
        value: Список UUID для валидации.
    Возвращаемое значение:
        Проверенный список UUID.
    Исключения:
        ValueError: Если список не пустой и содержит элементы, не являющиеся UUID.
    """
    if value is None:
        return None
    if value and not isinstance(value[0], UUID):
        raise ValueError(ERROR_EXECUTORS_MUST_BE_UUID_FORMAT)
    return value
