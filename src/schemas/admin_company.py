from datetime import date, datetime
from typing import Annotated, Literal, Optional, Self
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
    model_validator,
)

from src.models import CompanyUserRole
from src.schemas.constants import Length, Title
from src.schemas.validators.admin_company import (
    check_date_earlier_than_today,
    check_password_is_ascii,
    check_phone_number,
    check_start_date_earlier_than_end_date,
    check_telegram_username,
)

# Типизация для повторяющихся полей
date_and_validation = Annotated[date, AfterValidator(check_date_earlier_than_today)]
url_to_string = Annotated[HttpUrl, AfterValidator(str)]
NameField = Annotated[
    str,
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
OptionalNameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_NAME_LICENSE)
]
PhoneNumberField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_NAME, max_length=Length.MAX_PHONE_LENGTH)
]
TelegramUsernameField = Annotated[
    Optional[str],
    StringConstraints(min_length=Length.MIN_TELEGRAMM_USERNAME, max_length=Length.MAX_NAME_LICENSE)
]
AvatarLinkField = Annotated[
    Optional[url_to_string],
    Field(max_length=Length.MAX_FILE_LINK_LENGTH)
]

class AdminCompanyResponseSchema(BaseModel):
    """Схема компании для ответа админам сервиса.

    Поля:
        id: Идентификатор компании.
        name: Название компании.
        description: Описание компании (опционально).
        logo: Логотип компании (опционально).
        license_id: Номер лицензии (опционально).
        max_admins_count: Максимальное количество администраторов.
        max_employees_count: Максимальное количество сотрудников.
        start_license_time: Дата начала лицензии (опционально).
        end_license_time: Дата окончания лицензии (опционально).
        is_active: Активность лицензии.
        slug: Короткая строка для пути.
        created_at: Время создания.
        updated_at: Время обновления.
    """
    id: int
    name: str
    description: Optional[str]
    logo: Optional[HttpUrl]
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
    """Миксин для схем модераторов от компаний.

    Определяет общие поля и валидаторы.
    """
    patronymic: OptionalNameField = Field(None, title=Title.PATRONYMIC_USER)
    phone_number: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    birthday: Annotated[Optional[date_and_validation], Field(None, title=Title.BIRTHDAY_USER)]
    telegram_username: TelegramUsernameField = Field(None, title=Title.TELEGRAM_USERNAME)
    start_date_employment: Optional[date] = Field(None, title=Title.START_DATE_EMPLOYMENT_USER)
    end_date_employment: Optional[date] = Field(None, title=Title.END_DATE_EMPLOYMENT_USER)
    avatar_link: AvatarLinkField = Field(None, title=Title.AVATAR_LINK_USER)
    previous_department_id: Optional[int] = Field(None, title=Title.PREVIOUS_DEPARTMENT_ID_USER)
    employee_position: Optional[str] = Field(None, title=Title.EMPLOYEE_POSITION_USER)

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
    """Схема для чтения данных модераторов от компаний.

    Поля:
        id: Идентификатор пользователя.
        email: Электронная почта.
        name: Имя модератора.
        surname: Фамилия модератора.
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
        created_at: Время создания.
        updated_at: Время обновления.
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
    """Схема для полного обновления модераторов от компаний (PUT).

    Поля:
        name: Имя модератора (обязательно).
        surname: Фамилия модератора (обязательно).
        email: Электронная почта (обязательно).
        password: Пароль (обязательно).
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        birthday: Дата рождения (опционально).
        telegram_username: Имя в Telegram (опционально).
        role: Роль в компании (обязательно).
        current_department_id: Текущий отдел (обязательно).
        start_date_employment: Дата начала работы (опционально).
        end_date_employment: Дата окончания работы (опционально).
        avatar_link: Ссылка на аватар (опционально).
        previous_department_id: Предыдущий отдел (опционально).
        employee_position: Должность (опционально).
    """
    name: NameField = Field(..., title=Title.NAME_USER)
    surname: NameField = Field(..., title=Title.SURNAME_USER)
    role: CompanyUserRole
    current_department_id: int = Field(..., title=Title.CURRENT_DEPARTMENT_ID_USER)

class CompanyAdminCreateSchema(CompanyAdminPutSchema):
    """Схема для создания модераторов от компаний.

    Поля:
        name: Имя модератора (обязательно).
        surname: Фамилия модератора (обязательно).
        email: Электронная почта (обязательно).
        password: Пароль (обязательно).
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        birthday: Дата рождения (опционально).
        telegram_username: Имя в Telegram (опционально).
        role: Роль в компании (MODERATOR).
        current_department_id: Текущий отдел (обязательно).
        company_id: Идентификатор компании (обязательно).
        start_date_employment: Дата начала работы (опционально).
        end_date_employment: Дата окончания работы (опционально).
        avatar_link: Ссылка на аватар (опционально).
        previous_department_id: Предыдущий отдел (опционально).
        employee_position: Должность (опционально).
    """
    role: Literal[CompanyUserRole.MODERATOR]
    company_id: int = Field(..., title=Title.COMPANY_ID_USER)

class CompanyAdminPatchSchema(CompanyAdminSchemaMixin, BaseUserUpdate):
    """Схема для частичного обновления модераторов от компаний (PATCH).

    Поля:
        name: Имя модератора (опционально).
        surname: Фамилия модератора (опционально).
        email: Электронная почта (опционально).
        password: Пароль (опционально).
        patronymic: Отчество (опционально).
        phone_number: Номер телефона (опционально).
        birthday: Дата рождения (опционально).
        telegram_username: Имя в Telegram (опционально).
        role: Роль в компании (опционально).
        current_department_id: Текущий отдел (опционально).
        start_date_employment: Дата начала работы (опционально).
        end_date_employment: Дата окончания работы (опционально).
        avatar_link: Ссылка на аватар (опционально).
        previous_department_id: Предыдущий отдел (опционально).
        employee_position: Должность (опционально).
    """
    name: OptionalNameField = Field(None, title=Title.NAME_USER)
    surname: OptionalNameField = Field(None, title=Title.SURNAME_USER)
    role: Optional[CompanyUserRole] = None
    current_department_id: Optional[int] = Field(None, title=Title.CURRENT_DEPARTMENT_ID_USER)