from typing import Any, Callable

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.core.config.app import Settings


def get_tabit_openapi(app: FastAPI, settings: Settings) -> Callable:
    """Вернет расширенное OpenAPI приложения Tabit."""

    def tabit_openapi() -> dict[Any, Any]:
        """Расширенное OpenAPI приложения Tabit."""
        if not app.openapi_schema:
            openapi_schema = get_openapi(
                title=settings.app_title,
                description=settings.app_description,
                version=settings.version,
                routes=app.routes,
            )
            openapi_schema['components']['securitySchemes']['jwt_auth_backend_admin'] = {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
            app.openapi_schema = openapi_schema
        return app.openapi_schema

    return tabit_openapi
