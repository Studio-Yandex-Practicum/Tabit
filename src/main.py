from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from src.api.v1.routers import main_router
from src.config import settings
from src.logger import LoggingMiddleware
from src.scripts import application_management

app_v1 = FastAPI(
    title=settings.app_title,
    description=settings.description,
    version=settings.version,
    swagger_ui_parameters={'filter': True},
)
app_v1.middleware('http')(LoggingMiddleware())  # Add logging requests feature as middleware
app_v1.include_router(main_router)
settings.media_folder.mkdir(parents=True, exist_ok=True)
app_v1.mount(settings.media_url, StaticFiles(directory=settings.media_folder, html=True))
add_pagination(app_v1)



def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    application_management()


if __name__ == '__main__':
    main()
