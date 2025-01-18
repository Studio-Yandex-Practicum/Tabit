from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Tabit"
    description: str = "Tabit platform"

    db_type: str = "postgres"
    db_api: str = "asyncpg"
    db_user: str = "username"
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: str = "5433"
    db_name: str = "db_tabit"

    @property
    def database_url(self):
        return (
            f"{self.db_type}+{self.db_api}://"
            f"{self.db_user}:{self.db_password}@{self.db_host}"
            f"/{self.db_name}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
