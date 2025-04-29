import re
from datetime import date

from src.schemas.constants import TextError, Validation


def check_phone_number(phone_number: str) -> str:
    """
    Валидатор для проверки корректности формата номера телефона.

    Проверяет, что номер телефона соответствует российскому формату,
    определённому в Validation.PHONE_NUMBER_PATTERN.

    Аргументы:
        phone_number (str): Номер телефона для валидации.

    Возвращает:
        str: Проверенный номер телефона.

    Исключения:
        ValueError: Возникает, если номер телефона не соответствует российскому формату.
    """
    if not re.fullmatch(Validation.PHONE_NUMBER_PATTERN, phone_number):
        raise ValueError(TextError.INVALID_PHONE_NUMBER)
    return phone_number


def check_date_earlier_than_today(input_date: date) -> date:
    """
    Валидатор для проверки, что введённая дата не позже текущей.

    Проверяет, что указанная дата строго меньше или равна сегодняшней дате.

    Аргументы:
        input_date (date): Дата для валидации.

    Возвращает:
        date: Проверенная дата.

    Исключения:
        ValueError: Возникает, если дата позже текущей.
    """
    if input_date > date.today():
        raise ValueError(TextError.INVALID_DATE)
    return input_date


def check_start_date_earlier_than_end_date(start_date: date, end_date: date) -> None:
    """
    Валидатор для проверки порядка дат.

    Проверяет, что дата начала строго меньше даты окончания, если обе даты указаны.

    Аргументы:
        start_date (Optional[date]): Дата начала.
        end_date (Optional[date]): Дата окончания.

    Возвращает:
        None: Ничего не возвращает, если валидация успешна.

    Исключения:
        ValueError: Возникает, если дата начала не раньше даты окончания.
    """
    if any((start_date, end_date)) and start_date >= end_date:
        raise ValueError(TextError.INVALID_START_DATE)


def check_telegram_username(username: str) -> str:
    """
    Валидатор для проверки формата имени пользователя в Telegram.

    Проверяет, что имя пользователя состоит только из латинских букв, цифр и подчеркиваний,
    согласно Validation.TELEGRAM_USERNAME_PATTERN.

    Аргументы:
        username (str): Имя пользователя в Telegram для валидации.

    Возвращает:
        str: Проверенное имя пользователя.

    Исключения:
        ValueError: Возникает, если имя пользователя не соответствует допустимому формату.
    """
    if not re.fullmatch(Validation.TELEGRAM_USERNAME_PATTERN, username, flags=re.ASCII):
        raise ValueError(TextError.INVALID_TELEGRAM_USERNAME)
    return username


def check_password_is_ascii(password: str) -> str:
    """
    Валидатор для проверки, что пароль состоит только из ASCII-символов.

    Проверяет, что все символы в пароле принадлежат к набору ASCII.

    Аргументы:
        password (str): Пароль для валидации.

    Возвращает:
        str: Проверенный пароль.

    Исключения:
        ValueError: Возникает, если пароль содержит не-ASCII символы.
    """
    if not password.isascii():
        raise ValueError(TextError.INVALID_PASSWORD)
    return password
