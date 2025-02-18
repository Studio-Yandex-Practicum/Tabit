from fastapi import FastAPI

from src.api.v1.routers import main_router
from src.config import settings
from src.logger import LoggingMiddleware
from src.scripts import application_management

app_v1 = FastAPI(
    title=settings.app_title, description=settings.description, version=settings.version
)
app_v1.middleware('http')(LoggingMiddleware())  # Add logging requests feature as middleware
app_v1.include_router(main_router)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    application_management()


if __name__ == '__main__':
    main()
