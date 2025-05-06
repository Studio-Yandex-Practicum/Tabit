"""Модуль миксинов для схем приложения company."""

from typing import Any

from pydantic import model_validator


class GetterSlugMixin:
    """
    Миксин для генерации поля slug.

    Формирует поле `slug` на основе значения поля `name`.

    Валидаторы:
        get_slug: Генерирует slug из имени, если данные представлены в виде словаря.
    """

    @model_validator(mode='before')
    @classmethod
    def get_slug(cls, data: Any) -> Any:
        """Формирует `slug` на основе `name`."""
        # TODO: реализовать нормальное создание slug
        # TODO: проверить уникальность slug
        if isinstance(data, dict):
            data['slug'] = data['name']
        return data
