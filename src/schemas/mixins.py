"""Модуль миксинов для схем приложения company."""

from typing import Any, Optional
from datetime import date

from pydantic import Field, ConfigDict, model_validator

from src.core.constants.common import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
    MIN_LENGTH_NAME,
)
from src.core.constants.user import (
    TITLE_AVATAR_LINK_USER,
    TITLE_BIRTHDAY_USER,
    TITLE_CURRENT_DEPARTMENT_ID_USER,
    TITLE_DEPARTMENT_TRANSITION_DATE_USER,
    TITLE_EMPLOYEE_POSITION_USER,
    TITLE_END_DATE_EMPLOYMENT_USER,
    TITLE_LAST_DEPARTMENT_ID_USER,
    TITLE_PATRONYMIC_USER,
    TITLE_PHONE_NUMBER_USER,
    TITLE_START_DATE_EMPLOYMENT_USER,
    TITLE_TELEGRAM_USERNAME_USER,
)


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
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PATRONYMIC_USER,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=TITLE_PHONE_NUMBER_USER,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_BIRTHDAY_USER,
    )
    telegram_username: Optional[str] = Field(
        None,
        max_length=LENGTH_TELEGRAM_USERNAME,
        title=TITLE_TELEGRAM_USERNAME_USER,
    )
    start_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_START_DATE_EMPLOYMENT_USER,
    )
    end_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_END_DATE_EMPLOYMENT_USER,
    )
    avatar_link: Optional[str] = Field(
        None,
        max_length=LENGTH_FILE_LINK,
        title=TITLE_AVATAR_LINK_USER,
    )
    current_department_id: Optional[int] = Field(
        None,
        title=TITLE_CURRENT_DEPARTMENT_ID_USER,
    )
    last_department_id: Optional[int] = Field(
        None,
        title=TITLE_LAST_DEPARTMENT_ID_USER,
    )
    department_transition_date: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TITLE_DEPARTMENT_TRANSITION_DATE_USER,
    )
    employee_position: Optional[str] = Field(
        None,
        title=TITLE_EMPLOYEE_POSITION_USER,
    )
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
