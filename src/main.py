from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

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


def custom_openapi():
    if app_v1.openapi_schema:
        return app_v1.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_title,
        description=settings.description,
        version=settings.version,
        routes=app_v1.routes,
    )

    openapi_schema['components']['securitySchemes']['jwt_auth_backend_admin'] = {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT',
    }

    app_v1.openapi_schema = openapi_schema
    return app_v1.openapi_schema


app_v1.openapi = custom_openapi


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    application_management()


if __name__ == '__main__':
    main()
