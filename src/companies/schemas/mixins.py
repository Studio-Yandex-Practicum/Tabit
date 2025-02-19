"""Модуль миксинов для схем приложения company."""

from typing import Any

from pydantic import model_validator


class GetterSlugMixin:
    @model_validator(mode='before')
    @classmethod
    def get_slug(cls, data: Any) -> Any:
        """Метод для формирования `slug` объекта на основе его `name`."""
        # TODO: реализовать нормальное создание slug от названия
        # TODO: реализовать проверку уникальности slug - имя у компании не проверяется
        # на уникальность, а slug проверяется
        if isinstance(data, dict):
            data['slug'] = data['name']
        return data
