import re
from datetime import date

from src.tabit_management.constants import (
    VALID_INVALID_PASSWORD,
    VALID_INVALID_PHONE_NUMBER,
    VALID_INVALID_TELEGRAM_USERNAME,
    VALID_PHONE_NUMBER_PATTERN,
    VALID_WRONG_DATE,
)


def check_phone_number(phone_number: str) -> str:
    """
    Функция проверяет корректность формата введённого номера телефона.
    Паттерн разрешает только российские номера.
    """
    pattern = VALID_PHONE_NUMBER_PATTERN
    if not re.fullmatch(pattern, phone_number):
        raise ValueError(VALID_INVALID_PHONE_NUMBER)
    return phone_number


def check_date_earlier_than_today(input_date: date) -> date:
    """Функция проверяет, что введённая дата младше сегодняшней."""
    if input_date > date.today():
        raise ValueError(VALID_WRONG_DATE)
    return input_date


def check_telegram_username(username: str) -> str:
    """
    Функция проверят, что введённый telegram_username состоит только из латинских букв и цифр.
    """
    if not username.isalnum():
        raise ValueError(VALID_INVALID_TELEGRAM_USERNAME)
    return username


def check_password_is_ascii(password: str) -> str:
    """Функция проверят, что введённый пароль состоит только из символов ASCII."""
    if not password.isascii():
        raise ValueError(VALID_INVALID_PASSWORD)
    return password
