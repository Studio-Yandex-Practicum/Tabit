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

date_and_validation = Annotated[date, AfterValidator(check_date_earlier_than_today)]
url_to_string = Annotated[HttpUrl, AfterValidator(str)]


class AdminCompanyResponseSchema(BaseModel):
    """
    Схема компании для ответов админам сервиса.
    Параметры:
    - id: идентификатор компании (обязательно).
    - name: название компании (обязательно).
    - description: Описание компании (опционально).
    - logo: логотип (опционально).
    - license_id: номер лицензии (опционально).
    - max_admins_count: максимальное кол-во администраторов (обязательно).
    - max_employees_count: максимальное кол-во сотрудников (обязательно)
    - start_license_time: дата начала лицензии (опционально).
    - end_license_time: дата окончания действия лицензии (опционально).
    - is_active: bool - активна ли лицензия (обязательно).
    - slug: короткая строка для пути к эндпоинту компании (автозаполнение).
    - created_at: дата создания записи в таблице (автозаполнение).
    - updated_at: дата изменения записи в таблице (автозаполнение).
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
    """Схема-миксин для модераторов от компаний."""

    patronymic: Optional[str] = Field(
        None, min_length=Length.MIN_NAME, max_length=Length.MAX_NAME, title=Title.PATRONYMIC_USER
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.PHONE_NUMBER_USER,
    )
    birthday: Annotated[Optional[date_and_validation], Field(None, title=Title.BIRTHDAY_USER)]
    telegram_username: Optional[str] = Field(
        None,
        min_length=Length.MIN_TELEGRAMM_USERNAME,
        max_length=Length.MAX_TELEGRAM_USERNAME,
        title=Title.TELEGRAM_USERNAME,
    )
    start_date_employment: Optional[date] = Field(None, title=Title.START_DATE_EMPLOYMENT_USER)
    end_date_employment: Optional[date] = Field(None, title=Title.END_DATE_EMPLOYMENT_USER)
    avatar_link: Annotated[
        url_to_string, Field(None, max_length=Length.FILE_LINK, title=Title.AVATAR_LINK_USER)
    ]
    previous_department_id: Optional[int] = Field(
        None,
        title=Title.PREVIOUS_DEPARTMENT_ID_USER,
    )
    employee_position: Optional[str] = Field(
        None,
        title=Title.EMPLOYEE_POSITION_USER,
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
    """Схема для возврата данных модераторов от компаний при работе с ними."""

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
    """Схема для PUT-запроса изменения данных модераторов от компаний."""

    name: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_USER,
    )
    surname: str = Field(
        ...,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_USER,
    )
    role: CompanyUserRole
    current_department_id: int = Field(
        ...,
        title=Title.CURRENT_DEPARTMENT_ID_USER,
    )


class CompanyAdminCreateSchema(CompanyAdminPutSchema):
    """Схема для создания модераторов от компаний."""

    role: Literal[CompanyUserRole.MODERATOR]
    company_id: int = Field(
        ...,
        title=Title.COMPANY_ID_USER,
    )


class CompanyAdminPatchSchema(CompanyAdminSchemaMixin, BaseUserUpdate):
    """Схема для PATCH-запроса изменения данных модераторов от компаний."""

    name: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.NAME_USER,
    )
    surname: Optional[str] = Field(
        None,
        min_length=Length.MIN_NAME,
        max_length=Length.MAX_NAME,
        title=Title.SURNAME_USER,
    )
    role: Optional[CompanyUserRole] = None
    current_department_id: Optional[int] = Field(
        None,
        title=Title.CURRENT_DEPARTMENT_ID_USER,
    )
