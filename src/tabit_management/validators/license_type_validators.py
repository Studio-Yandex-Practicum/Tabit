from datetime import timedelta

from src.tabit_management.constants import (
    ERROR_FIELD_INTERVAL,
    ERROR_FIELD_START_OR_END_SPACE,
    LICENSE_TERM_REGEX,
)


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


def validate_license_term(value: int | str) -> timedelta | str:
    """
    Проверяет поле времени действия лицензии и конвертирует его в timedelta.

    Допустимые форматы:
        - "P1D" (1 день)
        - "P1Y" (1 год)
        - "P1Y1D" (1 год и 1 день)
        - Целое число (интерпретируется как дни)

    Args:
        value (int | str): Входное значение.

    Returns:
        timedelta | str: Обработанное значение (timedelta или исходная строка).

    Raises:
        ValueError: Если значение не соответствует допустимым форматам.
    """
    if isinstance(value, str):
        if value.isdigit():
            value = int(value)
        elif LICENSE_TERM_REGEX.match(value):
            return value

    if isinstance(value, int):
        return timedelta(days=value)

    raise ValueError(ERROR_FIELD_INTERVAL)
