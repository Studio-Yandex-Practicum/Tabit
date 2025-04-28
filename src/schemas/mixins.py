"""Модуль миксинов для схем приложения company."""

from datetime import date
from typing import Any, Optional

from pydantic import ConfigDict, Field, model_validator

from src.schemas.constants import Length, Title


class GetterSlugMixin:
    """Миксин, для генерации поля slug."""

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


class UserSchemaMixin:
    """Схема-миксин пользователя сервиса."""

    patronymic: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PATRONYMIC_USER,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PHONE_NUMBER_USER,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=Title.BIRTHDAY_USER,
    )
    telegram_username: Optional[str] = Field(
        None,
        max_length=Length.MAX_TELEGRAM_USERNAME,
        title=Title.TELEGRAM_USERNAME,
    )
    start_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=Title.START_DATE_EMPLOYMENT_USER,
    )
    end_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=Title.END_DATE_EMPLOYMENT_USER,
    )
    avatar_link: Optional[str] = Field(
        None,
        max_length=Length.FILE_LINK,
        title=Title.AVATAR_LINK_USER,
    )
    current_department_id: Optional[int] = Field(
        None,
        title=Title.CURRENT_DEPARTMENT_ID_USER,
    )
    previous_department_id: Optional[int] = Field(
        None,
        title=Title.PREVIOUS_DEPARTMENT_ID_USER,
    )
    department_transition_date: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=Title.DEPARTMENT_TRANSITION_DATE_USER,
    )
    employee_position: Optional[str] = Field(
        None,
        title=Title.EMPLOYEE_POSITION_USER,
    )
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
