from datetime import date, datetime
from typing import Annotated, Literal, Optional, Self
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from src.models.enum import CompanyUserRole
from src.schemas.annotations import (
    AvatarLinkField,
    NameField,
    OptionalNameField,
    PhoneNumberField,
    TelegramUsernameField,
    date_and_validation,
)
from src.schemas.constants import TitleConstants
from src.schemas.validators.admin_company import (
    check_password_is_ascii,
    check_phone_number,
    check_start_date_earlier_than_end_date,
    check_telegram_username,
)


class AdminCompanyResponseSchema(BaseModel):
    """
    Схема для возврата данных о компании администраторам сервиса Табит.

    Используется для возврата данных о компании в API для администраторов сервиса.

    Атрибуты:
        id (int): Идентификатор компании.
        name (str): Название компании.
        description (Optional[str]): Описание компании.
        logo (Optional[HttpUrl]): Логотип компании.
        license_id (Optional[int]): Номер лицензии.
        max_admins_count (int): Максимальное количество администраторов.
        max_employees_count (int): Максимальное количество сотрудников.
        start_license_time (Optional[datetime]): Дата начала лицензии.
        end_license_time (Optional[datetime]): Дата окончания лицензии.
        is_active (bool): Активность лицензии.
        slug (str): Короткая строка для пути.
        created_at (datetime): Время создания.
        updated_at (datetime): Время обновления.
    """

    id: int
    name: str
    description: Optional[str]
    logo: Optional[str]
    license_id: Optional[int]
    max_admins_count: int
    max_employees_count: int
    start_license_time: Optional[datetime]
    end_license_time: Optional[datetime]
    is_active: bool
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyAdminSchemaMixin:
    """
    Базовый миксин для схем администраторов компаний в сервисе Табит.

    Определяет общие поля и валидаторы для схем модераторов компаний.

    Атрибуты:
        patronymic (Optional[str]): Отчество модератора.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        employee_position (Optional[str]): Должность.

    Валидаторы:
        validate_phone_number: Проверяет формат номера телефона.
        validate_telegram_username: Проверяет формат имени в Telegram.
        validate_password: Проверяет, что пароль состоит из ASCII-символов.
        validate_start_date_end_date: Проверяет, что дата начала раньше даты окончания.
    """

    patronymic: OptionalNameField = Field(None, title=TitleConstants.PATRONYMIC_USER)
    phone_number: PhoneNumberField = Field(None, title=TitleConstants.PHONE_NUMBER_USER)
    birthday: Annotated[
        Optional[date_and_validation], Field(None, title=TitleConstants.BIRTHDAY_USER)
    ]
    telegram_username: TelegramUsernameField = Field(None, title=TitleConstants.TELEGRAM_USERNAME)
    start_date_employment: Optional[date] = Field(
        None, title=TitleConstants.START_DATE_EMPLOYMENT_USER
    )
    end_date_employment: Optional[date] = Field(
        None, title=TitleConstants.END_DATE_EMPLOYMENT_USER
    )
    avatar_link: AvatarLinkField = Field(None, title=TitleConstants.AVATAR_LINK_USER)
    previous_department_id: Optional[int] = Field(
        None, title=TitleConstants.PREVIOUS_DEPARTMENT_ID_USER
    )
    employee_position: Optional[str] = Field(None, title=TitleConstants.EMPLOYEE_POSITION_USER)

    model_config = ConfigDict(extra='forbid')

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """Проверяет формат номера телефона."""
        return check_phone_number(value)

    @field_validator('telegram_username')
    @classmethod
    def validate_telegram_username(cls, value: str) -> str:
        """Проверяет формат имени в Telegram."""
        return check_telegram_username(value)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Проверяет, что пароль состоит из ASCII-символов."""
        return check_password_is_ascii(value)

    @model_validator(mode='after')
    def validate_start_date_end_date(self) -> Self:
        """Проверяет, что дата начала раньше даты окончания."""
        check_start_date_earlier_than_end_date(
            self.start_date_employment, self.end_date_employment
        )
        return self


class CompanyAdminReadSchema(BaseUser[UUID]):
    """
    Схема для чтения данных администратора компании (GET).

    Используется для возврата данных о модераторах компаний в API.

    Атрибуты:
        id (UUID): Идентификатор пользователя.
        email (str): Электронная почта.
        name (str): Имя модератора.
        surname (str): Фамилия модератора.
        patronymic (Optional[str]): Отчество.
        phone_number (Optional[str]): Номер телефона.
        is_active (bool): Активность пользователя.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        role (str): Роль в компании.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        company_id (int): Идентификатор компании.
        current_department_id (Optional[int]): Идентификатор текущего отдела.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        department_transition_date (Optional[date]): Дата перехода в отдел.
        employee_position (Optional[str]): Должность.
        created_at (datetime): Время создания.
        updated_at (datetime): Время обновления.
    """

    name: str
    surname: str
    patronymic: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    birthday: Optional[date]
    telegram_username: Optional[str]
    role: str
    start_date_employment: Optional[date]
    end_date_employment: Optional[date]
    avatar_link: Optional[str]
    company_id: int
    current_department_id: Optional[int]
    previous_department_id: Optional[int]
    department_transition_date: Optional[date]
    employee_position: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyAdminPutSchema(CompanyAdminSchemaMixin, BaseUserCreate):
    """
    Схема для полного обновления администратора компании (PUT).

    Используется для обновления всех данных модератора компании через API.

    Атрибуты:
        name (str): Имя модератора.
        surname (str): Фамилия модератора.
        email (str): Электронная почта.
        password (str): Пароль.
        patronymic (Optional[str]): Отчество.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        role (CompanyUserRole): Роль в компании.
        current_department_id (int): Идентификатор текущего отдела.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        employee_position (Optional[str]): Должность.

    Валидаторы:
        Наследуются от CompanyAdminSchemaMixin.
    """

    name: NameField = Field(..., title=TitleConstants.NAME_USER)
    surname: NameField = Field(..., title=TitleConstants.SURNAME_USER)
    role: CompanyUserRole
    current_department_id: int = Field(..., title=TitleConstants.CURRENT_DEPARTMENT_ID_USER)


class CompanyAdminCreateSchema(CompanyAdminPutSchema):
    """
    Схема для создания нового администратора компании (POST).

    Используется для создания нового модератора компании через API.

    Атрибуты:
        name (str): Имя модератора.
        surname (str): Фамилия модератора.
        email (str): Электронная почта.
        password (str): Пароль.
        patronymic (Optional[str]): Отчество.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        role (Literal[CompanyUserRole.MODERATOR]): Роль в компании (MODERATOR).
        current_department_id (int): Идентификатор текущего отдела.
        company_id (int): Идентификатор компании.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        employee_position (Optional[str]): Должность.

    Валидаторы:
        Наследуются от CompanyAdminSchemaMixin.
    """

    role: Literal[CompanyUserRole.MODERATOR]
    company_id: int = Field(..., title=TitleConstants.COMPANY_ID_USER)


class CompanyAdminPatchSchema(CompanyAdminSchemaMixin, BaseUserUpdate):
    """
    Схема для частичного обновления администратора компании (PATCH).

    Используется для частичного обновления данных модератора компании через API.

    Атрибуты:
        name (Optional[str]): Имя модератора.
        surname (Optional[str]): Фамилия модератора.
        email (Optional[str]): Электронная почта.
        password (Optional[str]): Пароль.
        patronymic (Optional[str]): Отчество.
        phone_number (Optional[str]): Номер телефона.
        birthday (Optional[date]): Дата рождения.
        telegram_username (Optional[str]): Имя в Telegram.
        role (Optional[CompanyUserRole]): Роль в компании.
        current_department_id (Optional[int]): Идентификатор текущего отдела.
        start_date_employment (Optional[date]): Дата начала работы.
        end_date_employment (Optional[date]): Дата окончания работы.
        avatar_link (Optional[str]): Ссылка на аватар.
        previous_department_id (Optional[int]): Идентификатор предыдущего отдела.
        employee_position (Optional[str]): Должность.

    Валидаторы:
        Наследуются от CompanyAdminSchemaMixin.
    """

    name: OptionalNameField = Field(None, title=TitleConstants.NAME_USER)
    surname: OptionalNameField = Field(None, title=TitleConstants.SURNAME_USER)
    role: Optional[CompanyUserRole] = None
    current_department_id: Optional[int] = Field(
        None, title=TitleConstants.CURRENT_DEPARTMENT_ID_USER
    )
