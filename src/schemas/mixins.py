"""Модуль миксинов для схем приложения company."""

from datetime import date
from typing import Any, Optional

from pydantic import ConfigDict, Field, model_validator

from src.schemas.constants import LengthConstants, TitleConstants


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
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.PATRONYMIC_USER,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=LengthConstants.MIN_NAME,
        max_length=LengthConstants.MAX_NAME,
        title=TitleConstants.PHONE_NUMBER_USER,
    )
    birthday: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TitleConstants.BIRTHDAY_USER,
    )
    telegram_username: Optional[str] = Field(
        None,
        max_length=LengthConstants.MAX_TELEGRAM_USERNAME,
        title=TitleConstants.TELEGRAM_USERNAME,
    )
    start_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TitleConstants.START_DATE_EMPLOYMENT_USER,
    )
    end_date_employment: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TitleConstants.END_DATE_EMPLOYMENT_USER,
    )
    avatar_link: Optional[str] = Field(
        None,
        max_length=LengthConstants.FILE_LINK,
        title=TitleConstants.AVATAR_LINK_USER,
    )
    current_department_id: Optional[int] = Field(
        None,
        title=TitleConstants.CURRENT_DEPARTMENT_ID_USER,
    )
    previous_department_id: Optional[int] = Field(
        None,
        title=TitleConstants.PREVIOUS_DEPARTMENT_ID_USER,
    )
    department_transition_date: Optional[date] = Field(
        None,
        # TODO: проверка на корректность даты рождения.
        title=TitleConstants.DEPARTMENT_TRANSITION_DATE_USER,
    )
    employee_position: Optional[str] = Field(
        None,
        title=TitleConstants.EMPLOYEE_POSITION_USER,
    )
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
