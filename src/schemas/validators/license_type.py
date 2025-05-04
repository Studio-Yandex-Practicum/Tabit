from datetime import timedelta

from src.schemas.constants import TextErrorConstants, ValidationConstants


def validate_string(value: str) -> str:
    """
    Валидатор для проверки строкового поля на наличие пробелов.

    Проверяет, что строка не содержит пробелов в начале или конце.

    Аргументы:
        value (str): Строковое значение для валидации.

    Возвращает:
        str: Проверенная строка.

    Исключения:
        ValueError: Возникает, если строка содержит пробелы в начале или конце.
    """
    if value != value.strip():
        raise ValueError(TextErrorConstants.FIELD_START_OR_END_SPACE)
    return value


def validate_license_term(value: int | str) -> timedelta | str:
    """
    Валидатор для проверки и конвертации срока действия лицензии.

    Проверяет, что входное значение соответствует допустимому формату срока действия лицензии
        и конвертирует его в объект timedelta.
    Допустимые форматы:
        - Целое число (интерпретируется как количество дней, например, 30).
        - Строка в формате ISO 8601
            (например, "P1Y" для 1 года, "P1D" для 1 дня, "P1Y1D" для 1 года и 1 дня).

    Аргументы:
        value (int | str): Срок действия лицензии (число дней или строка в формате ISO 8601).

    Возвращает:
        timedelta: Объект timedelta, представляющий срок действия лицензии.

    Исключения:
        ValueError: Возникает, если значение не соответствует допустимым форматам.
    """
    if isinstance(value, str):
        if value.isdigit():
            value = int(value)
        elif ValidationConstants.LICENSE_TERM_REGEX.match(value):
            return value

    if isinstance(value, int):
        return timedelta(days=value)

    raise ValueError(TextErrorConstants.FIELD_INTERVAL)
