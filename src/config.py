import os

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


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
    log_level: str = 'DEBUG'

    jwt_secret: SecretStr = 'SUPERSECRETKEY'
    jwt_lifetime_seconds: int = 32400  # 9 часов: смена + обед.

    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.db_host}:{self.port_bd_postgres}'
            f'/{self.postgres_db}'
        )

    class Config:
        env_file = '.env'


settings = Settings()
