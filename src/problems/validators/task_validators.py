from datetime import date
from typing import List

from sqlalchemy import UUID

from src.problems.constants import ERROR_EXECUTORS_MUST_BE_UUID_FORMAT, ERROR_TASK_NAME_EMPTY


def validate_date_in_future(value: date) -> date:
    """Дата должна быть в будущем"""
    if value < date.today():
        raise ValueError('Дата должна быть в будущем')
    return value


def validate_name(value: str) -> str:
    """Проверка, что имя не пустое"""
    if value.strip() == '':
        raise ValueError(ERROR_TASK_NAME_EMPTY)
    return value


def validate_executors(value: List[UUID]) -> List[UUID]:
    """Проверка, что исполнители предоставлены правильно"""
    if value and not isinstance(value[0], UUID):
        raise ValueError(ERROR_EXECUTORS_MUST_BE_UUID_FORMAT)
    return value
