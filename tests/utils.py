from typing import Any
from uuid import UUID


def is_valid_uuid(value: Any) -> bool:
    """Вернет True если переданное значение является UUID, иначе вернет False."""
    try:
        UUID(str(value))
        return True
    except ValueError:
        return False
