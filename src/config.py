from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Tabit'
    description: str = 'Tabit platform'
    version: str = '1.0.0'
    db_type: str = 'postgres'
    db_api: str = 'asyncpg'
    postgres_user: str = 'username'
    postgres_password: SecretStr = 'password'
    postgres_db: str = 'db_tabit'
    port_bd_postgres: str = '5433'
    db_host: str = 'localhost'


    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.postgres_user}:{self.postgres_password}@{self.db_host}'
            f'/{self.postgres_db}'
        )

    class Config:
        env_file = '.env'


settings = Settings()
