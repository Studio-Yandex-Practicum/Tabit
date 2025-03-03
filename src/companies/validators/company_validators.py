"""
Модуль валидаторов приложения companies.
"""

import re
from typing import Optional, Self

from pydantic import HttpUrl

from src.companies.constants import (
    TEST_ERROR_INVALID_CHARACTERS_NAME,
    TEST_ERROR_INVALID_CHARACTERS_SURNAME,
    TEST_ERROR_LICENSE_FIELDS,
    TEST_ERROR_UNIQUE_NAME_SURNAME,
)
from src.tabit_management.constants import ERROR_FIELD_START_OR_END_SPACE


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


def validate_slug(slug: Optional[str]) -> Optional[str]:
    """
    Проверяет, соответствует ли переданный slug допустимому формату.

    Разрешены только латинские буквы, цифры и дефисы.
    Пример корректного slug: 'example-company-123'.

    :param slug: Строка слага, переданная для проверки.
    :return: Возвращает slug, если он соответствует требованиям, или None.
    :raises ValueError: Если slug содержит недопустимые символы.
    """
    if slug and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        raise ValueError('Slug может содержать только латинские буквы, цифры и дефисы.')
    return slug


def check_license_fields_none(values: Self) -> Self:
    """
    Проверяет корректность заполнения полей лицензии.

    Либо оба поля (`license_id` и `start_license_time`) должны быть заполнены,
    либо оба должны быть пустыми. Нельзя оставить одно из них незаполненным.

    :param values: Экземпляр модели, содержащий данные о лицензии.
    :return: Возвращает неизмененный объект, если проверка пройдена.
    :raises ValueError: Если одно поле заполнено, а второе нет.
    """
    if not (
        all((values.license_id, values.start_license_time))
        or (all((not values.license_id, not values.start_license_time)))
    ):
        raise ValueError(TEST_ERROR_LICENSE_FIELDS)
    return values


def validate_logo(logo: Optional[str]) -> Optional[str]:
    """
    Проверяет, является ли переданный логотип (`logo`) корректным URL-адресом.

    Функция принимает строку с URL-адресом логотипа компании и выполняет валидацию.
    Если URL некорректен, вызывается исключение `ValueError`.

    Допустимые примеры:
    - "https://example.com/logo.png"
    - "http://my-site.org/images/logo.jpg"

    Недопустимые примеры:
    - "string" (не является URL)
    - "ftp://files.com/logo.png" (не HTTP/HTTPS)
    - "/local/path/to/logo.png" (относительный путь)

    :param logo: Строка, содержащая URL-адрес логотипа (может быть None).
    :return: Возвращает строку URL, если валидация пройдена, иначе вызывает исключение.
    :raises ValueError: Если `logo` не является корректным URL-адресом.
    """
    if logo is not None:
        try:
            HttpUrl(logo)
        except ValueError:
            raise ValueError('Логотип должен быть валидным URL-адресом.')
    return logo


def validate_string(value: str) -> str:
    """
    Проверяет строковое поле на наличие пробелов в начале или конце.

    Args:
        value (str): Входное строковое значение.

    Returns:
        str: Очищенное от пробелов значение.

    Raises:
        ValueError: Если строка содержит пробелы в начале или в конце.
    """
    if value != value.strip():
        raise ValueError(ERROR_FIELD_START_OR_END_SPACE)
    return value
