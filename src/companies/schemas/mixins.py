from typing import Any

from pydantic import model_validator


class GetterSlugMixin:
    """Миксин, для генерации поля slug."""

    @model_validator(mode='before')
    @classmethod
    def get_slug(cls, data: Any) -> Any:
        """Сгенерирует поле slug."""
        # TODO: реализовать нормальное создание slug от названия
        # TODO: реализовать проверку уникальности slug - имя у компании не проверяется
        # на уникальность, а slug проверяется
        if isinstance(data, dict):
            data['slug'] = data['name']
        return data
