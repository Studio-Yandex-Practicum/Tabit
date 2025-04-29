"""Модуль миксинов для схем приложения company."""

from datetime import date
from typing import Optional

from pydantic import ConfigDict, Field

from src.schemas.annotations import (
    AvatarLinkField,
    NameField,
    PhoneNumberField,
    TelegramUsernameField,
)
from src.schemas.constants import Title


class UserSchemaMixin:
    """
    Миксин для схем пользователей сервиса.

    Определяет дополнительные поля для схем пользователей компании.

    Атрибуты:
        patronymic (Optional[str]): Отчество пользователя.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        current_department_id (Optional[int]): Идентификатор текущего отдела.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        department_transition_date (Optional[date]): Дата перехода в отдел.
        employee_position (Optional[str]): Должность.
    """

    patronymic: NameField = Field(None, title=Title.PATRONYMIC_USER)
    phone_number: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    birthday: Optional[date] = Field(None, title=Title.BIRTHDAY_USER)  # TODO: валидация даты
    telegram_username: TelegramUsernameField = Field(None, title=Title.TELEGRAM_USERNAME)
    start_date_employment: Optional[date] = Field(None, title=Title.START_DATE_EMPLOYMENT_USER)
    end_date_employment: Optional[date] = Field(None, title=Title.END_DATE_EMPLOYMENT_USER)
    avatar_link: AvatarLinkField = Field(None, title=Title.AVATAR_LINK_USER)
    current_department_id: Optional[int] = Field(None, title=Title.CURRENT_DEPARTMENT_ID_USER)
    previous_department_id: Optional[int] = Field(None, title=Title.PREVIOUS_DEPARTMENT_ID_USER)
    department_transition_date: Optional[date] = Field(
        None, title=Title.DEPARTMENT_TRANSITION_DATE_USER
    )
    employee_position: Optional[str] = Field(None, title=Title.EMPLOYEE_POSITION_USER)

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
