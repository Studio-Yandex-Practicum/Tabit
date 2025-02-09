from pydantic import BaseModel, Field

from src.constants import DEFAULT_LIMIT, DEFAULT_SKIP


class BaseFilterSchema(BaseModel):
    """
    Базовая схема фильтраций.

    Используется для обработки query-параметров:
    пагинация, сортировка и фильтрация списка объектов.
    """

    skip: int = Field(DEFAULT_SKIP, ge=0, title='Пропустить n объектов')
    limit: int = Field(DEFAULT_LIMIT, ge=1, title='Лимитировать список объектов')
    # TODO добавить поля для сортировки и фильтрации


class CompanyFilterSchema(BaseFilterSchema):
    """Фильтр списка компаний под query-параметры."""

    # TODO добавить валидацию query-параметров сортировки и фильтрации


class UserFilterSchema(BaseFilterSchema):
    """Фильтр списка пользователей под query-параметры."""

    # TODO добавить валидацию query-параметров сортировки и фильтрации
