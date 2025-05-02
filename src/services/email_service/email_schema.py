from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.services.email_service.constants import (
    LengthConstants,
    TextErrorConstants,
    TitleConstants,
)


class EmailCreateSchema(BaseModel):
    """Cхема для создания электронного письма."""

    email: List[EmailStr] = Field(..., title=TitleConstants.EMAIL_NAME)
    subject_email: str = Field(
        ..., max_length=LengthConstants.MAX_EMAIL, title=TitleConstants.SUBJECT_EMAIL
    )
    message: str = Field(..., title=TitleConstants.USER_MESSAGE)

    @field_validator('message')
    @classmethod
    def validate_empty_message(cls, value: str) -> str:
        if value == '':
            raise ValueError(TextErrorConstants.CAN_NOT_EMPTY_STRING)
        return value
