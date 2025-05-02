from datetime import date
from typing import List
from uuid import UUID

from src.schemas.constants import TextErrorConstants


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
    if value < date.today():
        raise ValueError(f'{TextErrorConstants.DATE_SHOULD_BE_FUTURE} {date.today()}')
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
    if not value.strip():
        raise ValueError(TextErrorConstants.TASK_NAME_EMPTY)
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
    if not value:
        return []
    for executor_id in value:
        if not isinstance(executor_id, UUID):
            raise ValueError(TextErrorConstants.EXECUTORS_MUST_BE_UUID_FORMAT)
    return value
