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
    """Проверяет, что имя и фамилия не совпадают."""
    if name and surname and name == surname:
        raise ValueError(TEST_ERROR_UNIQUE_NAME_SURNAME)


def validate_name_characters(name: Optional[str]) -> None:
    """Проверяет, что имя содержит только буквы."""
    if name and not name.isalpha():
        raise ValueError(TEST_ERROR_INVALID_CHARACTERS_NAME)


def validate_surname_characters(surname: Optional[str]) -> None:
    """Проверяет, что фамилия содержит только буквы."""
    if surname and not surname.isalpha():
        raise ValueError(TEST_ERROR_INVALID_CHARACTERS_SURNAME)


def validate_license_fields(
    license_id: Optional[int], start_license_time: Optional[datetime]
) -> None:
    """
    Проверяет, что поля лицензии либо оба заполнены, либо оба пусты.
    """
    if not (
        all((license_id, start_license_time)) or all((not license_id, not start_license_time))
    ):
        raise ValueError(TEST_ERROR_LICENSE_FIELDS)
