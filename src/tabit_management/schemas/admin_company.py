from datetime import date, datetime
from typing import Annotated, Literal, Optional
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from src.constants import (
    LENGTH_FILE_LINK,
    LENGTH_NAME_USER,
    LENGTH_TELEGRAM_USERNAME,
    MIN_LENGTH_NAME,
    MIN_LENGTH_TELEGRAM_USERNAME,
)
from src.tabit_management.validators.admin_company_validators import (
    check_date_earlier_than_today,
    check_password_is_ascii,
    check_phone_number,
    check_start_date_earlier_than_end_date,
    check_telegram_username,
)
from src.users.constants import (
    title_avatar_link_user,
    title_birthday_user,
    title_company_id_user,
    title_current_department_id_user,
    title_employee_position_user,
    title_end_date_employment_user,
    title_last_department_id_user,
    title_name_user,
    title_patronymic_user,
    title_phone_number_user,
    title_start_date_employment_user,
    title_surname_user,
    title_telegram_username_user,
)
from src.users.models.enum import RoleUserTabit

date_and_validation = Annotated[date, AfterValidator(check_date_earlier_than_today)]
url_to_string = Annotated[HttpUrl, AfterValidator(str)]


class AdminCompanyResponseSchema(BaseModel):
    """
    Параметры:
        id: Идентификатор компании.
        name: Название.
        description: Описание (опционально).
        logo: Логотип (опционально).
        license_id: Ссылка на тип лицензии (опционально).
        max_admins_count: Максимальное кол-во администраторов.
        max_employees_count: Максимальное кол-во сотрудников.
        start_license_time: Дата начала действия лицензии (опционально).
        end_license_time: Дата окончания действия лицензии (опционально).
        is_active: активна ли лицензия.
        slug: Короткая строка для пути к эндпоинту.
        created_at: Дата создания.
        updated_at: Дата изменения.
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

    model_config = ConfigDict(
        from_attributes=True,
        title = "Схема ответа админам",
        description = "Схема компании для ответов админам сервиса"
    )


class CompanyAdminSchemaMixin:
    """Схема-миксин для админов от компаний."""

    patronymic: Optional[str] = Field(
        None, min_length=MIN_LENGTH_NAME, max_length=LENGTH_NAME_USER, title=title_patronymic_user
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_phone_number_user,
    )
    birthday: Annotated[Optional[date_and_validation], Field(None, title=title_birthday_user)]
    telegram_username: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_TELEGRAM_USERNAME,
        max_length=LENGTH_TELEGRAM_USERNAME,
        title=title_telegram_username_user,
    )
    start_date_employment: Optional[date] = Field(None, title=title_start_date_employment_user)
    end_date_employment: Optional[date] = Field(None, title=title_end_date_employment_user)
    avatar_link: Annotated[
        url_to_string, Field(None, max_length=LENGTH_FILE_LINK, title=title_avatar_link_user)
    ]
    last_department_id: Optional[int] = Field(
        None,
        title=title_last_department_id_user,
    )
    employee_position: Optional[str] = Field(
        None,
        title=title_employee_position_user,
    )

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return check_phone_number(value)

    @field_validator('telegram_username')
    @classmethod
    def validate_telegram_username(cls, value: str) -> str:
        return check_telegram_username(value)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        return check_password_is_ascii(value)

    @model_validator(mode='after')
    def validate_start_date_end_date(self) -> Self:
        check_start_date_earlier_than_end_date(
            self.start_date_employment, self.end_date_employment
        )
        return self


class CompanyAdminReadSchema(BaseUser[UUID]):
    """
    Параметры:
        name: Имя пользователя сервиса.
        surname: Фамилия пользователя сервиса.
        patronymic: Отчество пользователя сервиса(опционально).
        phone_number: Контактный телефон пользователя сервиса(опционально).
        is_active: Активен ли пользователь.
        birthday: День рождение пользователя(опционально).
        telegram_username: Имя пользователя в Telegram.
        role: Роль пользователя.
        start_date_employment: Дата начала работы сотрудника(опционально).
        end_date_employment: Дата окончания работы сотрудника(опционально).
        avatar_link: Ссылка на аватар пользователя(опционально).
        company_id: Идентефикатор компании пользователя.
        current_department_id: Идентефикатор отдела пользователя(опционально).
        last_department_id: Идентефикатор предыдущего отдела пользователя(опционально).
        department_transition_date: Дата последнего перехода между отделами(опционально).
        employee_position: Позиция в коллективе(опционально).
        created_at: Дата создания профиля пользователя.
        updated_at: Дата обновления профиля пользователя.
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
    last_department_id: Optional[int]
    department_transition_date: Optional[date]
    employee_position: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        title = "Схема для админов",
        description = "Схема для возврата данных админов от компаний"
    )


class CompanyAdminPutSchema(CompanyAdminSchemaMixin, BaseUserCreate):
    """
    Параметры:
        name: Имя пользователя сервиса.
        surname: Фамилия пользователя сервиса.
        role: Роль пользователя.
        current_department_id: Идентефикатор отдела пользователя(опционально).
    """

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_user,
    )
    surname: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_user,
    )
    role: RoleUserTabit
    current_department_id: int = Field(
        ...,
        title=title_current_department_id_user,
    )

    model_config = ConfigDict(
        title = "Схема PUT-запроса",
        description = "Схема для PUT-запроса изменения данных админов от компаний"
    )


class CompanyAdminCreateSchema(CompanyAdminPutSchema):
    """
    Параметры:
        role: Роль пользователя.
        company_id: Идентефикатор компании пользователя.
    """

    role: Literal[RoleUserTabit.ADMIN]
    company_id: int = Field(
        ...,
        title=title_company_id_user,
    )

    model_config = ConfigDict(
        title = "Схема создания админов",
        description = "Схема для создания админов от компаний"
    )


class CompanyAdminPatchSchema(CompanyAdminSchemaMixin, BaseUserUpdate):
    """
    Параметры:
        name: Имя пользователя сервиса.
        surname: Фамилия пользователя сервиса.
        role: Роль пользователя.
        current_department_id: Идентефикатор отдела пользователя(опционально).
    """

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_user,
    )
    surname: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_surname_user,
    )
    role: Optional[RoleUserTabit] = None
    current_department_id: Optional[int] = Field(
        None,
        title=title_current_department_id_user,
    )

    model_config = ConfigDict(
        title = "Схема обновления данных",
        description = "Схема для изменения данных админов от компаний"
    )
