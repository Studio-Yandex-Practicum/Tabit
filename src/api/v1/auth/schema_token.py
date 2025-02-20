from pydantic import BaseModel


class TokenReadSchemas(BaseModel):
    """Схема ответа получения JWT-токенов."""

    token_type: str
    access_token: str
    refresh_token: str
