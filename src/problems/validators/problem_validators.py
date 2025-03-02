from src.problems.constants import ERROR_PROBLEM_NAME_EMPTY


def validate_not_empty(value: str) -> str:
    """Проверка, что значение не пустое и не состоит только из пробелов.

    Назначение:
        Валидирует, что строка:
        1. Не является пустой
        2. Не состоит только из пробелов
    Параметры:
        value: Значение для валидации.
    Возвращаемое значение:
        Проверенное значение.
    Исключения:
        ValueError: Если значение пустое или состоит только из пробелов.
    """
    if not value.strip():
        raise ValueError(ERROR_PROBLEM_NAME_EMPTY)
    return value.strip()
