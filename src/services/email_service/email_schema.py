from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.services.email_service.constants import Length, TextError, Title


class EmailCreateSchema(BaseModel):
    """Cхема для создания электронного письма."""

    email: List[EmailStr] = Field(..., title=Title.EMAIL_NAME)
    subject_email: str = Field(..., max_length=Length.MAX_EMAIL, title=Title.SUBJECT_EMAIL)
    message: str = Field(..., title=Title.USER_MESSAGE)

    @field_validator('message')
    @classmethod
    def validate_empty_message(cls, value: str) -> str:
        if value == '':
            raise ValueError(TextError.CAN_NOT_EMPTY_STRING)
        return value
