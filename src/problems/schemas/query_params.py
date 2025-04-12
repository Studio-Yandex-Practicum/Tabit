"""
Временный файл для реализации ограничения выборки для GET-запросов, возвращающих список объектов.
По-хорошему необходимо реализовать пагинацию в общем файле и применять её к эндпоинтам.
"""

from pydantic import BaseModel, ConfigDict, Field

from src.constants import DEFAULT_LIMIT, DEFAULT_SKIP


class FeedsFilterSchema(BaseModel):
    """
    Параметры:
        skip: пропуск объектов.
        limit: ограничить список объектов.
    """

    skip: int = Field(DEFAULT_SKIP, ge=0, title='Пропустить n объектов')
    limit: int = Field(DEFAULT_LIMIT, ge=1, title='Лимитировать список объектов')
    # TODO: добавить поля для сортировки и фильтрации

    model_config = ConfigDict(
        title='Базовая схема фильтраций',
        description='Используется для обработки query-параметров:'
        'пагинация, сортировка и фильтрация списка объектов',
    )
