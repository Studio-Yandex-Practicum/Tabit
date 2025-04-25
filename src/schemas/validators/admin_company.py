import re
from datetime import date

from src.schemas.constants import TextError, Validation


def check_phone_number(phone_number: str) -> str:
    """
    Функция проверяет корректность формата введённого номера телефона.
    Паттерн разрешает только российские номера.
    """
    if not re.fullmatch(Validation.PHONE_NUMBER_PATTERN, phone_number):
        raise ValueError(TextError.INVALID_PHONE_NUMBER)
    return phone_number


def check_date_earlier_than_today(input_date: date) -> date:
    """Функция проверяет, что введённая дата младше сегодняшней."""
    if input_date > date.today():
        raise ValueError(TextError.INVALID_DATE)
    return input_date


def check_start_date_earlier_than_end_date(start_date: date, end_date: date) -> None:
    """Функция проверяет, что переданный параметр start_date строго меньше end_date."""
    if any((start_date, end_date)) and start_date >= end_date:
        raise ValueError(TextError.INVALID_START_DATE)


def check_telegram_username(username: str) -> str:
    """
    Функция проверяет, что введённый telegram_username состоит только из латинских букв и цифр.
    """
    if not re.fullmatch(Validation.TELEGRAM_USERNAME_PATTERN, username, flags=re.ASCII):
        raise ValueError(TextError.INVALID_TELEGRAM_USERNAME)
    return username


def check_password_is_ascii(password: str) -> str:
    """Функция проверяет, что введённый пароль состоит только из символов ASCII."""
    if not password.isascii():
        raise ValueError(TextError.INVALID_PASSWORD)
    return password
