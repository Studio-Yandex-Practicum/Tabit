from pydantic import SecretStr
from pydantic_settings import BaseSettings
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend


class Settings(BaseSettings):
    app_title: str = 'Tabit'
    description: str = 'Tabit platform'
    version: str = '1.0.0'
    db_type: str = 'postgres'
    db_api: str = 'asyncpg'
    db_user: str = 'username'
    db_password: SecretStr = 'password'
    db_host: str = 'localhost'
    db_name: str = 'db_tabit'

    jwt_secret: SecretStr = 'SUPERSECRETKEY'
    jwt_lifetime_seconds: int = 3600

    @property
    def database_url(self):
        return (
            f'{self.db_type}+{self.db_api}://'
            f'{self.db_user}:{self.db_password}@{self.db_host}'
            f'/{self.db_name}'
        )

    class Config:
        env_file = '.env'


settings = Settings()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret.get_secret_value(),
        lifetime_seconds=settings.jwt_lifetime_seconds,
    )


jwt_auth_backend = AuthenticationBackend(
    name='jwt',
    transport=None,
    get_strategy=get_jwt_strategy,
)
