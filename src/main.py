from fastapi import FastAPI

from src.api.v1.routers import main_router
from src.core.config.app import settings
from src.core.config.logging import LoggingMiddleware
from scripts.pre_start import application_management

app_v1 = FastAPI(
    title=settings.app_title,
    description=settings.description,
    version=settings.version,
    swagger_ui_parameters={'filter': True},
)
app_v1.middleware('http')(LoggingMiddleware())  # Add logging requests feature as middleware
app_v1.include_router(main_router)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    application_management()


if __name__ == '__main__':
    main()
