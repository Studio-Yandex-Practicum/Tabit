from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Tabit"
    description: str = "Tabit platform"
    database_url: str = "postgresql+asyncpg://admin:password@localhost/db_tabit"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
