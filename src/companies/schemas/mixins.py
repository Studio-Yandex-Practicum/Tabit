"""Модуль миксинов для схем приложения company."""

from typing import Any

from pydantic import model_validator


class GetterSlugMixin:
    """Миксин, для генерации поля slug."""

    @model_validator(mode='before')
    @classmethod
    def get_slug(cls, data: Any) -> Any:
        """Метод для формирования `slug` объекта на основе его `name`."""
        if isinstance(data, dict):
            data['slug'] = data['name']
        return data
