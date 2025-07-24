from pydantic import BaseModel


class ForgotPasswordRequest(BaseModel):
    """Схема для запроса восстановления пароля"""

    email: str


class ResetPasswordRequest(BaseModel):
    """Схема для сброса пароля"""

    token: str
    new_password: str


class ForceResetPasswordRequest(BaseModel):
    """Схема для принудительного сброса пароля"""

    new_password: str


class ChangePasswordRequest(BaseModel):
    """Схема для смены пароля"""

    current_password: str
    new_password: str
