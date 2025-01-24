from enum import StrEnum


class RoleUserTabit(StrEnum):
    """Варианты значений поля role модели UserTabit."""

    ADMIN = 'Админ'
    EMPLOYEE = 'Сотрудник'
