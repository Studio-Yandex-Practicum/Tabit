"""
Модуль валидаторов приложения companies.
"""

from datetime import datetime
from typing import Optional

from src.companies.constants import (
    TEST_ERROR_INVALID_CHARACTERS_NAME,
    TEST_ERROR_INVALID_CHARACTERS_SURNAME,
    TEST_ERROR_LICENSE_FIELDS,
    TEST_ERROR_UNIQUE_NAME_SURNAME,
)


def validate_name_surname_unique(name: Optional[str], surname: Optional[str]) -> None:
    """
    Проверяет, что имя и фамилия не совпадают.
    Args:
        name Optional[str]: имя пользователя.
        surname Optional[str]: фамилия пользователя.
    Raises:
        ValueError: Если имя совпадает с фамилией, вызывается ошибка.
    """
    if name and surname and name == surname:
        raise ValueError(TEST_ERROR_UNIQUE_NAME_SURNAME)


def validate_name_characters(name: Optional[str]) -> None:
    """
    Проверяет, что имя содержит только буквы.
    Args:
        name Optional[str]: имя пользователя.
    Raises:
        ValueError: Если имя содержит запрещенные символы,
        вызывается ошибка.
    """
    if name and not name.isalpha():
        raise ValueError(TEST_ERROR_INVALID_CHARACTERS_NAME)


def validate_surname_characters(surname: Optional[str]) -> None:
    """
    Проверяет, что фамилия содержит только буквы.
     Args:
        surname Optional[str]: фамилия пользователя.
    Raises:
        ValueError: Если фамилия содержит запрещенные символы,
        вызывается ошибка.
    """
    if surname and not surname.isalpha():
        raise ValueError(TEST_ERROR_INVALID_CHARACTERS_SURNAME)


def validate_license_fields(
    license_id: Optional[int], start_license_time: Optional[datetime]
) -> None:
    """
    Проверяет, что поля лицензии либо оба заполнены, либо оба пусты.
    Args:
        license_id: Optional[int]: номер лицензии.
        start_license_time Optional[datetime]: время начала лицензии.
    Raises:
        ValueError: одно поле заполнено, а второе нет,
        вызывается ошибка.
    """
    if not (
        all((license_id, start_license_time)) or all((not license_id, not start_license_time))
    ):
        raise ValueError(TEST_ERROR_LICENSE_FIELDS)
