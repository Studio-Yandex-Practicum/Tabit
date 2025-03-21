import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from pydantic import ConfigDict, EmailStr, SecretStr
from pydantic_settings import BaseSettings

from src.constants import BASE_DIR

load_dotenv()


class Settings(BaseSettings):
    app_title: str = 'Tabit'
    description: str = 'Tabit platform'
    version: str = '1.0.0'
    db_type: str = 'postgres'
    db_api: str = 'asyncpg'
    db_host: str = os.getenv('DB_HOST')
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    postgres_db: str = os.getenv('POSTGRES_DB')
    port_bd_postgres: str = os.getenv('PORT_BD_POSTGRES')
    log_level: str = os.getenv('LOG_LEVEL')

    jwt_secret: SecretStr = 'SUPERSECRETKEY'
    jwt_lifetime_seconds: int = 3_600  # 1 час.
    jwt_lifetime_seconds_refresh: int = 86_400  # 24 часа.
    jwt_token_type: str = 'bearer'
    jwt_token_algorithm: str = 'HS256'  # TODO: спрятать в .env
    jwt_token_audience: list[str] = ['fastapi-users:auth']  # TODO: спрятать в .env
    jwt_distinguishing_feature_access_token: str = 'access'  # TODO: спрятать в .env
    jwt_distinguishing_feature_refresh_token: str = 'refresh'  # TODO: спрятать в .env

    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None
    first_superuser_name: str | None = None
    first_superuser_surname: str | None = None

    mail_username: str | None = None
    mail_password: str | None = None
    mail_from: str | None = None
    mail_port: str | None = None
    mail_server: str | None = None
    mail_from_name: str | None = None
    mail_starttls: bool = True  # Для соединений STARTTLS (шифрование).
    mail_ssl_tls: bool = False  # Для подключения по протоколу TLS / SSL.
    use_credentials: bool = True  # По умолчанию True. Подключаться к SMTP-серверу или нет.
    validate_certs: bool = True  # Cледует ли проверять сертификат почтового сервера.
    template_folder: Path = BASE_DIR / 'templates'

    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.db_host}:{self.port_bd_postgres}'
            f'/{self.postgres_db}'
        )

    model_config = ConfigDict(env_file='.env', extra='ignore')


settings = Settings()


class EmailSettings:
    """Класс для настройки подключения отправки электронной почты."""

    @property
    def config_email(self) -> ConnectionConfig:
        if not all(
            [
                settings.mail_username,
                settings.mail_password,
                settings.mail_from,
                settings.mail_port,
                settings.mail_server,
                settings.mail_from_name,
            ]
        ):
            raise ValueError('Не все необходимые настройки электронной почты предоставлены')

        return ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_FROM_NAME=settings.mail_from_name,
            MAIL_STARTTLS=settings.mail_starttls,
            MAIL_SSL_TLS=settings.mail_ssl_tls,
            USE_CREDENTIALS=settings.use_credentials,
            VALIDATE_CERTS=settings.validate_certs,
            TEMPLATE_FOLDER=settings.template_folder,
        )


email_settings = EmailSettings()
