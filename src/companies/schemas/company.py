from datetime import datetime
from typing import Optional

from fastapi_users.schemas import BaseUserUpdate
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from src.companies.constants import TEST_ERROR_LICENSE_FIELDS
from src.companies.schemas.mixins import GetterSlugMixin
from src.constants import LENGTH_NAME_COMPANY, MIN_LENGTH_NAME
from src.users.schemas import UserSchemaMixin


class CompanyUpdateForUserSchema(BaseModel):
    """Схема для частичного изменения компании пользователем-админом."""

    description: Optional[str] = Field(
        None,
        title='',
    )
    logo: Optional[str] = Field(
        None,
        title='',
    )


class CompanyUpdateSchema(CompanyUpdateForUserSchema):
    """Схема для частичного изменения компании админом сервиса."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title='',
    )
    license_id: Optional[int] = Field(
        None,
        title='',
    )
    start_license_time: Optional[datetime] = Field(
        None,
        title='',
    )

    @model_validator(mode='after')
    def check_license_fields_none(self) -> Self:
        """
        При присвоении лицензии необходимо указать и её начало.
        Нельзя, что бы одно поле было не заполнено.
        """
        if not (
            all((self.license_id, self.start_license_time))
            or (all((not self.license_id, not self.start_license_time)))
        ):
            raise ValueError(TEST_ERROR_LICENSE_FIELDS)
        return self


class CompanyCreateSchema(GetterSlugMixin, CompanyUpdateSchema):
    """Схема для создания компании."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title='',
    )
    slug: str = Field(..., title='')


class CompanyResponseSchema(BaseModel):
    """Схема компании для ответов админам сервиса."""

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


class CompanyDepartmentUpdateSchema(BaseModel, GetterSlugMixin):
    """Схема для обновления данных об отделе."""

    name: Optional[str] = Field(
        None,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title='',
    )
    slug: Optional[str] = Field(None, title='')

    model_config = ConfigDict(extra='forbid')


class CompanyDepartmentCreateSchema(CompanyDepartmentUpdateSchema):
    """Схема для создания отдела."""

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_COMPANY,
        title='',
    )

    model_config = ConfigDict(from_attributes=True)


class CompanyDepartmentResponseSchema(CompanyDepartmentCreateSchema):
    """Схема для получения данных отдела."""

    id: int
    name: str
    slug: str
    company_id: int


class CompanyUserDepartmentUpdateSchema(UserSchemaMixin, BaseUserUpdate):
    """Схема для изменения данных сотрудника компании."""


# class CompanyUserDepartmentUpdateSchema(BaseModel):
#    """Схема для изменения департамента сотрудника компании."""
#
#    current_department_id: int = Field(..., alias='current_department_id')
#    last_department_id: int = Field(..., alias='last_department_id')
