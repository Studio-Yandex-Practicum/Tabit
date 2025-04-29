"""
Модуль валидаторов приложения companies.
"""

import re
from typing import Optional, Self

from pydantic import HttpUrl

from src.schemas.constants import TextError


def validate_name_surname_unique(name: Optional[str], surname: Optional[str]) -> None:
    """
    Валидатор для проверки уникальности имени и фамилии.

    Проверяет, что имя и фамилия пользователя не совпадают, если оба поля заполнены.

    Аргументы:
        name (Optional[str]): Имя пользователя.
        surname (Optional[str]): Фамилия пользователя.

    Возвращает:
        None: Ничего не возвращает, если валидация успешна.

    Исключения:
        ValueError: Возникает, если имя и фамилия совпадают.
    """
    if name and surname and name == surname:
        raise ValueError(TextError.UNIQUE_NAME_SURNAME)


def validate_name_characters(name: Optional[str]) -> None:
    """
    Валидатор для проверки корректности символов в имени.

    Проверяет, что имя содержит только буквы, если оно указано.

    Аргументы:
        name (Optional[str]): Имя пользователя.

    Возвращает:
        None: Ничего не возвращает, если валидация успешна.

    Исключения:
        ValueError: Возникает, если имя содержит недопустимые символы.
    """
    if name and not name.isalpha():
        raise ValueError(TextError.INVALID_CHARACTERS_NAME)


def validate_surname_characters(surname: Optional[str]) -> None:
    """
    Валидатор для проверки корректности символов в фамилии.

    Проверяет, что фамилия содержит только буквы, если она указана.

    Аргументы:
        surname (Optional[str]): Фамилия пользователя.

    Возвращает:
        None: Ничего не возвращает, если валидация успешна.

    Исключения:
        ValueError: Возникает, если фамилия содержит недопустимые символы.
    """
    if surname and not surname.isalpha():
        raise ValueError(TextError.INVALID_CHARACTERS_SURNAME)


def validate_slug(slug: Optional[str]) -> Optional[str]:
    """
    Валидатор для проверки формата slug.

    Проверяет, что slug содержит только латинские буквы, цифры и дефисы, и соответствует формату
        (например, 'example-company-123').

    Аргументы:
        slug (Optional[str]): Строка slug для валидации.

    Возвращает:
        Optional[str]: Проверенный slug или None, если входное значение None.

    Исключения:
        ValueError: Возникает, если slug содержит недопустимые символы или имеет неверный формат.
    """
    if slug and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        raise ValueError('Slug может содержать только латинские буквы, цифры и дефисы.')
    return slug


def check_license_fields_none(values: Self) -> Self:
    """
    Валидатор для проверки корректности заполнения полей лицензии.

    Проверяет, что поля `license_id` и `start_license_time` либо оба заполнены, либо оба пусты.

    Аргументы:
        values (Self): Экземпляр Pydantic-модели с данными лицензии.

    Возвращает:
        Self: Неизмененный экземпляр модели, если валидация успешна.

    Исключения:
        ValueError: Возникает, если одно из полей заполнено, а другое пусто.
    """
    if not (
        all((values.license_id, values.start_license_time))
        or (all((not values.license_id, not values.start_license_time)))
    ):
        raise ValueError(TextError.LICENSE_FIELDS)
    return values


def validate_logo(logo: Optional[str]) -> Optional[str]:
    """
    Валидатор для проверки корректности URL логотипа компании.

    Проверяет, что переданная строка, если она указана, является валидным URL-адресом
    с протоколом HTTP или HTTPS
    (например, для изображений логотипов, размещенных на внешних серверах).
    Это необходимо для корректного отображения логотипа в веб-приложении и предотвращения
    ошибок при загрузке ресурсов.

    Допустимые примеры:
    - "https://example.com/logo.png" (валидный HTTPS URL для изображения)
    - "http://my-site.org/images/logo.jpg" (валидный HTTP URL для изображения)
    - None (отсутствие логотипа, допустимо)

    Недопустимые примеры:
    - "string" (не является URL)
    - "ftp://files.com/logo.png" (использует неподдерживаемый протокол FTP)
    - "/local/path/to/logo.png" (относительный путь, не является полноценным URL)

    Аргументы:
        logo (Optional[str]): Строка с URL-адресом логотипа
            (может быть None, если логотип не указан).

    Возвращает:
        Optional[str]: Проверенный URL логотипа или None, если входное значение None.

    Исключения:
        ValueError: Возникает, если строка не является валидным URL-адресом с протоколом HTTP/HTTPS
            (например, при использовании других протоколов или некорректного формата).
    """
    if logo is not None:
        try:
            HttpUrl(logo)
        except ValueError:
            raise ValueError('Логотип должен быть валидным URL-адресом.')
    return logo


def validate_string(value: str) -> str:
    """
    Валидатор для проверки строкового поля на пробелы.

    Проверяет, что строка не содержит пробелов в начале или конце.

    Аргументы:
        value (str): Строковое значение для валидации.

    Возвращает:
        str: Проверенная строка.

    Исключения:
        ValueError: Возникает, если строка содержит пробелы в начале или конце.
    """
    if value != value.strip():
        raise ValueError(TextError.FIELD_START_OR_END_SPACE)
    return value
