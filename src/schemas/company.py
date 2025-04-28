from datetime import datetime
from typing import Literal, Optional, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from src.schemas.constants import MiscConstants, Title
from src.schemas.types import (
    CompanyNameField,
    DescriptionField,
    FeedbackQuestionField,
    NameField,
    OptionalCompanyNameField,
    PhoneNumberField,
    TelegramUsernameField,
)
from src.schemas.user import UserUpdateSchema
from src.schemas.validators.company import (
    check_license_fields_none,
    validate_name_characters,
    validate_name_surname_unique,
    validate_slug,
    validate_string,
    validate_surname_characters,
)


class CompanyUpdateForUserSchema(BaseModel):
    """Схема для обновления компании пользователем-админом.

    Поля:
        description: Описание компании (опционально).
        logo: Логотип компании (опционально).
    """
    description: DescriptionField = Field(None, title=Title.NAME_COMPANY)
    logo: Optional[str] = Field(None, title=Title.LOGO_COMPANY)

    model_config = ConfigDict(extra='forbid')

    @field_validator('description', mode='after', check_fields=False)
    @classmethod
    def validate_description(cls, value: str) -> str:
        """Проверяет отсутствие пробелов в начале или конце описания."""
        return validate_string(value)

class CompanyUpdateSchema(CompanyUpdateForUserSchema):
    """Схема для обновления компании админом сервиса.

    Поля:
        name: Название компании (опционально).
        description: Описание компании (опционально).
        logo: Логотип компании (опционально).
        license_id: Номер лицензии (опционально).
        start_license_time: Дата начала лицензии (опционально).
        end_license_time: Дата окончания лицензии (опционально).
    """
    name: OptionalCompanyNameField = Field(None, title=Title.NAME_COMPANY)
    license_id: Optional[int] = Field(None, title=Title.LICENSE_ID_COMPANY)
    start_license_time: Optional[datetime] = Field(
        None,
        title=Title.START_LICENSE_TIME_COMPANY,
    )
    end_license_time: Optional[datetime] = None

    @field_validator('name', mode='after', check_fields=False)
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Проверяет отсутствие пробелов в начале или конце названия."""
        return validate_string(value)

    @model_validator(mode='after')
    def validate_license_fields(self) -> Self:
        """Проверяет корректность заполнения полей лицензии."""
        return check_license_fields_none(self)

class CompanyCreateSchema(CompanyUpdateSchema):
    """Схема для создания компании.

    Поля:
        name: Название компании (обязательно).
        description: Описание компании (опционально).
        logo: Логотип компании (опционально).
        license_id: Номер лицензии (опционально).
        start_license_time: Дата начала лицензии (опционально).
        end_license_time: Дата окончания лицензии (опционально).
        slug: Короткая строка для пути (опционально).
    """
    name: CompanyNameField = Field(..., title=Title.NAME_COMPANY)
    slug: Optional[str] = Field(None, title=Title.SLUG_COMPANY)

    @field_validator('slug')
    @classmethod
    def check_slug(cls, slug: Optional[str]) -> Optional[str]:
        """Проверяет формат slug (латинские буквы, цифры, дефисы)."""
        return validate_slug(slug)

class CompanyResponseSchema(BaseModel):
    """Схема компании для ответа.

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

class CompanyTypeFilterSchema(BaseModel):
    """Схема фильтрации списка компаний.

    Поля:
        name: Фильтр по названию компании (опционально).
        ordering: Сортировка по полям (опционально).
    """
    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)

    model_config = ConfigDict(extra='forbid')

class CompanyDepartmentUpdateSchema(BaseModel):
    """Схема для обновления отдела.

    Поля:
        name: Название отдела (обязательно).
    """
    name: CompanyNameField = Field(..., title=Title.NAME_DEPARTMENT)

    model_config = ConfigDict(extra='forbid')

class CompanyDepartmentCreateSchema(CompanyDepartmentUpdateSchema):
    """Схема для создания отдела.

    Поля:
        name: Название отдела (обязательно).
    """
    model_config = ConfigDict(extra='forbid', from_attributes=True)

class CompanyDepartmentResponseSchema(BaseModel):
    """Схема для ответа с данными отдела.

    Поля:
        id: Идентификатор отдела.
        name: Название отдела.
        slug: Короткая строка для пути.
        company_id: Идентификатор компании.
    """
    id: int
    name: str
    slug: str
    company_id: int

    model_config = ConfigDict(from_attributes=True)

class CompanyEmployeeUpdateSchema(UserUpdateSchema):
    """Схема для обновления сотрудника админом компании.

    Поля унаследованы от UserUpdateSchema.
    """
    @model_validator(mode='after')
    def validate_fields(self) -> Self:
        """Проверяет уникальность и формат имени и фамилии."""
        validate_name_surname_unique(self.name, self.surname)
        validate_name_characters(self.name)
        validate_surname_characters(self.surname)
        return self

class UserCompanyUpdateSchema(BaseModel):
    """Схема для редактирования профиля сотрудником компании.

    Поля:
        name: Имя сотрудника (опционально).
        surname: Фамилия сотрудника (опционально).
        phone_number: Номер телефона (опционально).
        email: Электронная почта (опционально).
        telegram_username: Имя в Telegram (опционально).
    """
    name: NameField = Field(None, title=Title.NAME_USER)
    surname: NameField = Field(None, title=Title.SURNAME_USER)
    phone_number: PhoneNumberField = Field(None, title=Title.PHONE_NUMBER_USER)
    email: Optional[EmailStr] = None
    telegram_username: TelegramUsernameField = Field(None, title=Title.TELEGRAM_USERNAME)

    @model_validator(mode='after')
    def validate_fields(self) -> Self:
        """Проверяет уникальность и формат имени и фамилии."""
        validate_name_surname_unique(self.name, self.surname)
        validate_name_characters(self.name)
        validate_surname_characters(self.surname)
        return self

class CompanyFeedbackCreateSchema(BaseModel):
    """Схема для создания обратной связи.

    Поля:
        question: Вопрос для обратной связи (обязательно).
    """
    question: FeedbackQuestionField = Field(..., title='Задать вопрос для обратной связи')

    model_config = ConfigDict(from_attributes=True)