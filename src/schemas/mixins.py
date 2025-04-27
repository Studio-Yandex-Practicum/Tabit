"""Модуль миксинов для схем приложения company."""

from datetime import date
from typing import Annotated, Any, Optional

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from src.schemas.constants import Length, Title

NameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
PhoneNumberField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
TelegramUsernameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_TELEGRAM_USERNAME, max_length=Length.MAX_TELEGRAM_USERNAME)
]
AvatarLinkField = Annotated[
    Optional[str],
    StringConstraints(max_length=Length.FILE_LINK)
]

class GetterSlugMixin:
    """Миксин для генерации поля slug."""

    @model_validator(mode='before')
    @classmethod
    def get_slug(cls, data: Any) -> Any:
        """Формирует `slug` на основе `name`."""
        # TODO: реализовать нормальное создание slug
        # TODO: проверить уникальность slug
        if isinstance(data, dict):
            data['slug'] = data['name']
        return data

class UserSchemaMixin:
    """Миксин для схем пользователей сервиса.

    Поля:
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        birthday: Дата рождения (опционально).
        telegram_username: Имя в Telegram (опционально).
        start_date_employment: Дата начала работы (опционально).
        end_date_employment: Дата окончания работы (опционально).
        avatar_link: Ссылка на аватар (опционально).
        current_department_id: Текущий отдел (опционально).
        previous_department_id: Предыдущий отдел (опционально).
        department_transition_date: Дата перехода в отдел (опционально).
        employee_position: Должность (опционально).
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