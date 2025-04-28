from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field

from src.models import CompanyUserRole
from src.schemas import UserSchemaMixin
from src.schemas.constants import Title
from src.schemas.types import (
    AvatarLinkField,
    NameField,
    OptionalNameField,
    PhoneNumberField,
    TelegramUsernameField,
)


class UserReadSchema(BaseUser[UUID]):
    """Схема пользователя сервиса для ответов.

    Поля:
        id: Идентификатор пользователя.
        email: Электронная почта.
        name: Имя пользователя.
        surname: Фамилия пользователя.
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        is_active: Активность пользователя.
        birthday: Дата рождения (опционально).
        telegram_username: Имя в Telegram (опционально).
        role: Роль в компании.
        start_date_employment: Дата начала работы (опционально).
        end_date_employment: Дата окончания работы (опционально).
        avatar_link: Ссылка на аватар (опционально).
        company_id: Идентификатор компании.
        current_department_id: Текущий отдел (опционально).
        previous_department_id: Предыдущий отдел (опционально).
        department_transition_date: Дата перехода в отдел (опционально).
        employee_position: Должность (опционально).
        created_at: Время создания (опционально).
        updated_at: Время обновления (опционально).
    """
    name: str = Field(..., title=Title.NAME_USER)
    surname: str = Field(..., title=Title.SURNAME_USER)
    patronymic: Optional[str] = Field(None, title=Title.PATRONYMIC_USER)
    phone_number: Optional[str] = Field(None, title=Title.PHONE_NUMBER_USER)
    is_active: bool = Field(..., title=Title.IS_ACTIVE_USER)
    birthday: Optional[date] = Field(None, title=Title.BIRTHDAY_USER)
    telegram_username: Optional[str] = Field(None, title=Title.TELEGRAM_USERNAME)
    role: str = Field(..., title=Title.ROLE_USER)
    start_date_employment: Optional[date] = Field(None, title=Title.START_DATE_EMPLOYMENT_USER)
    end_date_employment: Optional[date] = Field(None, title=Title.END_DATE_EMPLOYMENT_USER)
    avatar_link: Optional[str] = Field(None, title=Title.AVATAR_LINK_USER)
    company_id: int = Field(..., title=Title.COMPANY_ID_USER)
    current_department_id: Optional[int] = Field(None, title=Title.CURRENT_DEPARTMENT_ID_USER)
    previous_department_id: Optional[int] = Field(None, title=Title.PREVIOUS_DEPARTMENT_ID_USER)
    department_transition_date: Optional[date] = Field(
        None, title=Title.DEPARTMENT_TRANSITION_DATE_USER
    )
    employee_position: Optional[str] = Field(None, title=Title.EMPLOYEE_POSITION_USER)
    created_at: Optional[datetime] = Field(None, title=Title.CREATED_AT_USER)
    updated_at: Optional[datetime] = Field(None, title=Title.UPDATED_AT_USER)

    model_config = ConfigDict(from_attributes=True)

class UserCreateSchema(UserSchemaMixin, BaseUserCreate):
    """Схема для создания пользователя сервиса.

    Поля:
        name: Имя пользователя (обязательно).
        surname: Фамилия пользователя (обязательно).
        email: Электронная почта (обязательно).
        password: Пароль (обязательно).
        role: Роль в компании (по умолчанию EMPLOYEE).
        company_id: Идентификатор компании (обязательно).
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
    name: NameField = Field(..., title=Title.NAME_USER)
    surname: NameField = Field(..., title=Title.SURNAME_USER)
    role: CompanyUserRole = Field(CompanyUserRole.EMPLOYEE, title=Title.ROLE_USER)
    company_id: int = Field(..., title=Title.COMPANY_ID_USER)

class UserUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """Схема для изменения данных пользователя сервиса.

    Поля:
        name: Имя пользователя (опционально).
        surname: Фамилия пользователя (опционально).
        email: Электронная почта (опционально).
        password: Пароль (опционально).
        role: Роль в компании (опционально).
        company_id: Идентификатор компании (опционально).
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
    name: OptionalNameField = Field(None, title=Title.NAME_USER)
    surname: OptionalNameField = Field(None, title=Title.SURNAME_USER)
    role: Optional[CompanyUserRole] = Field(None, title=Title.ROLE_USER)
    company_id: Optional[int] = Field(None, title=Title.COMPANY_ID_USER)

class ResetPasswordByAdmin(BaseModel):
    """Схема для сброса пароля администратором.

    Поля:
        password: Новый пароль.
    """
    password: str

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class UserForUserUpdateSchema(BaseModel):
    """Схема для обновления данных пользователя сервиса.

    Поля:
        name: Имя пользователя (опционально).
        surname: Фамилия пользователя (опционально).
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        birthday: Дата рождения (опционально).
        telegram_username: Имя в Telegram (опционально).
        avatar_link: Ссылка на аватар (опционально).
    """
    name: OptionalNameField = Field(None, title=Title.NAME_USER)
    surname: OptionalNameField = Field(None, title=Title.SURNAME_USER)
    patronymic: OptionalNameField = Field(None, title=Title.PATRONYMIC_USER)
    phone_number: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    birthday: Optional[date] = Field(None, title=Title.BIRTHDAY_USER)
    telegram_username: TelegramUsernameField = Field(None, title=Title.TELEGRAM_USERNAME)
    avatar_link: AvatarLinkField = Field(None, title=Title.AVATAR_LINK_USER)

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)