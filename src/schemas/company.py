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

from src.schemas.annotations import (
    CompanyNameField,
    DescriptionField,
    FeedbackQuestionField,
    NameField,
    OptionalCompanyNameField,
    PhoneNumberField,
    TelegramUsernameField,
)
from src.schemas.constants import MiscConstants, Title
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
    """
    Схема для обновления компании пользователем-админом.

    Используется для изменения данных компании администратором компании через API.

    Атрибуты:
        description (Optional[str]): Описание компании.
        logo (Optional[str]): Логотип компании.

    Валидаторы:
        validate_description: Проверяет отсутствие пробелов в начале или конце описания.
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
    """
    Схема для обновления компании админом сервиса.

    Используется для изменения данных компании администратором сервиса через API.

    Атрибуты:
        name (Optional[str]): Название компании.
        description (Optional[str]): Описание компании.
        logo (Optional[str]): Логотип компании.
        license_id (Optional[int]): Номер лицензии.
        start_license_time (Optional[datetime]): Дата начала лицензии.
        end_license_time (Optional[datetime]): Дата окончания лицензии.

    Валидаторы:
        validate_name: Проверяет отсутствие пробелов в начале или конце названия.
        validate_license_fields: Проверяет корректность заполнения полей лицензии.
    """

    name: OptionalCompanyNameField = Field(None, title=Title.NAME_COMPANY)
    license_id: Optional[int] = Field(None, title=Title.LICENSE_ID_COMPANY)
    start_license_time: Optional[datetime] = Field(
        None,
        title=TitleConstants.START_LICENSE_TIME_COMPANY,
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
    """
    Схема для создания компании.

    Используется для создания новой компании через API.

    Атрибуты:
        name (str): Название компании.
        description (Optional[str]): Описание компании.
        logo (Optional[str]): Логотип компании.
        license_id (Optional[int]): Номер лицензии.
        start_license_time (Optional[datetime]): Дата начала лицензии.
        end_license_time (Optional[datetime]): Дата окончания лицензии.
        slug (Optional[str]): Короткая строка для пути.

    Валидаторы:
        check_slug: Проверяет формат slug (латинские буквы, цифры, дефисы).
        validate_name: Проверяет отсутствие пробелов в начале или конце названия.
        validate_license_fields: Проверяет корректность заполнения полей лицензии.
    """

    name: CompanyNameField = Field(..., title=Title.NAME_COMPANY)
    slug: Optional[str] = Field(None, title=Title.SLUG_COMPANY)

    @field_validator('slug')
    @classmethod
    def check_slug(cls, slug: Optional[str]) -> Optional[str]:
        """Проверяет формат slug (латинские буквы, цифры, дефисы)."""
        return validate_slug(slug)


class CompanyResponseSchema(BaseModel):
    """
    Схема компании для ответа.

    Используется для возврата данных о компании в API.

    Атрибуты:
        id (int): Идентификатор компании.
        name (str): Название компании.
        description (Optional[str]): Описание компании.
        logo (Optional[str]): Логотип компании.
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


class CompanyTypeFilterSchema(BaseModel):
    """
    Схема фильтрации списка компаний.

    Используется для фильтрации и сортировки списка компаний в API.

    Атрибуты:
        name (Optional[str]): Фильтр по названию компании.
        ordering (Optional[str]): Сортировка по полям
            (name, created_at, updated_at, с префиксом '-' для обратной сортировки).
    """

    name: Optional[str] = Field(None, description=MiscConstants.FILTER_NAME_DESCRIPTION)
    ordering: Optional[
        Literal['name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at']
    ] = Field(None, description=MiscConstants.SORTING_DESCRIPTION)

    model_config = ConfigDict(extra='forbid')


class CompanyDepartmentUpdateSchema(BaseModel):
    """
    Схема для обновления отдела.

    Используется для изменения названия отдела через API.

    Атрибуты:
        name (str): Название отдела.
    """

    name: CompanyNameField = Field(..., title=Title.NAME_DEPARTMENT)

    model_config = ConfigDict(extra='forbid')


class CompanyDepartmentCreateSchema(CompanyDepartmentUpdateSchema):
    """
    Схема для создания отдела.

    Используется для создания нового отдела через API.

    Атрибуты:
        name (str): Название отдела.
    """

    model_config = ConfigDict(extra='forbid', from_attributes=True)


class CompanyDepartmentResponseSchema(BaseModel):
    """
    Схема для ответа с данными отдела.

    Используется для возврата данных об отделе в API.

    Атрибуты:
        id (int): Идентификатор отдела.
        name (str): Название отдела.
        slug (str): Короткая строка для пути.
        company_id (int): Идентификатор компании.
    """

    id: int
    name: str
    slug: str
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class CompanyEmployeeUpdateSchema(UserUpdateSchema):
    """
    Схема для обновления сотрудника админом компании.

    Используется для изменения данных сотрудника администратором компании через API.

    Атрибуты:
        Унаследованы от UserUpdateSchema.

    Валидаторы:
        validate_fields: Проверяет уникальность и формат имени и фамилии.
    """

    @model_validator(mode='after')
    def validate_fields(self) -> Self:
        """Проверяет уникальность и формат имени и фамилии."""
        validate_name_surname_unique(self.name, self.surname)
        validate_name_characters(self.name)
        validate_surname_characters(self.surname)
        return self


class UserCompanyUpdateSchema(BaseModel):
    """
    Схема для редактирования профиля сотрудником компании.

    Используется для обновления профиля сотрудника компании через API.

    Атрибуты:
        name (Optional[str]): Имя сотрудника.
        surname (Optional[str]): Фамилия сотрудника.
        phone_number (Optional[str]): Номер телефона.
        email (Optional[EmailStr]): Электронная почта.
        telegram_username (Optional[str]): Имя в Telegram.

    Валидаторы:
        validate_fields: Проверяет уникальность и формат имени и фамилии.
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
    """
    Схема для создания обратной связи.

    Используется для отправки вопроса по обратной связи через API.

    Атрибуты:
        question (str): Вопрос для обратной связи.
    """

    question: FeedbackQuestionField = Field(..., title='Задать вопрос для обратной связи')

    model_config = ConfigDict(from_attributes=True)
