from uuid import UUID

from src.users.constants import ERROR_TAG_NAME_EMPTY, ERROR_USER_MUST_BE_UUID_FORMAT


def validate_name(value: str) -> str:
    """Валидирует название тэга.

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
    if value is None:
        return None
    if not value.strip():
        raise ValueError(ERROR_TAG_NAME_EMPTY)
    return value.strip()


def validate_uuid_user(value: UUID) -> UUID:
    """Валидирует индификатор пользователя.

    Назначение:
        Валидирует, что значение:
        1. Не пустое (если передан)
        2. Является элементом типа UUID
    Параметры:
        value: Элемент UUID для валидации.
    Возвращаемое значение:
        Проверенный UUID.
    Исключения:
        ValueError: Если значение не пустое и является элементом, не являющимся UUID.
    """
    if value is None:
        return None
    if value and not isinstance(value, UUID):
        raise ValueError(ERROR_USER_MUST_BE_UUID_FORMAT)
    return value
