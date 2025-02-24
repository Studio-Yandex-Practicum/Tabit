from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.utils.email_service.constants_email import (
    MAX_LENGTH_SUBJECT_EMAIL,
    TITLE_EMAIL_MESSAGE,
    TITLE_EMAIL_NAME,
    TITLE_SUBJECT_EMAIL,
    VALUE_ERROR_EMPTY,
)


class EmailCreateSchema(BaseModel):
    """Cхема для создания электронного письма."""

    email: List[EmailStr] = Field(..., title=TITLE_EMAIL_NAME)
    subject_email: str = Field(..., max_length=MAX_LENGTH_SUBJECT_EMAIL, title=TITLE_SUBJECT_EMAIL)
    message: str = Field(..., title=TITLE_EMAIL_MESSAGE)

    @field_validator('message')
    @classmethod
    def validate_unique_name_surname(cls, value: str) -> str:
        if value == '':
            raise ValueError(VALUE_ERROR_EMPTY)
        return value
