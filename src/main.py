import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from scripts.pre_start import application_management
from src.admin import all_admin_views
from src.admin.auth import AdminAuth
from src.api.v1.routers import main_router
from src.core.config.app import settings
from src.core.config.logging import LoggingMiddleware
from src.core.database.db_depends import engine
from src.openapi import get_tabit_openapi

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(32)

app_v1 = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.version,
    swagger_ui_parameters={'filter': True},
)
app_v1.middleware('http')(LoggingMiddleware())  # Add logging requests feature as middleware
app_v1.include_router(main_router)
settings.media_folder.mkdir(parents=True, exist_ok=True)
app_v1.mount(settings.media_url, StaticFiles(directory=settings.media_folder, html=True))
app_v1.openapi = get_tabit_openapi(app_v1, settings)
app_v1.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app_v1, engine, authentication_backend=authentication_backend)
for view in all_admin_views:
    admin.add_view(view)


def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    application_management()


if __name__ == '__main__':
    main()
