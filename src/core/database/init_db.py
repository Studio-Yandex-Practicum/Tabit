from contextlib import asynccontextmanager

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from src.core.auth.access_to_db import get_admin_db
from src.core.auth.managers import get_admin_manager
from src.core.config.app import settings
from src.core.database.db_depends import get_async_session
from src.schemas import AdminCreateFirstSchema

get_async_session_context = asynccontextmanager(get_async_session)
get_admin_db_context = asynccontextmanager(get_admin_db)
get_admin_manager_context = asynccontextmanager(get_admin_manager)


async def create_superuser(
    email: EmailStr,
    password: str,
    name: str,
    surname: str,
    is_superuser: bool = True,
):
    """
    Корутина, создающая администратора-суперпользователя сервиса с переданными email и паролем.

    Если такой администратор уже есть - ничего не делает.
    """
    try:
        async with get_async_session_context() as session:
            async with get_admin_db_context(session) as admin_db:
                async with get_admin_manager_context(admin_db) as admin_manager:
                    await admin_manager.create(
                        AdminCreateFirstSchema(
                            email=email,
                            password=password,
                            is_superuser=is_superuser,
                            name=name,
                            surname=surname,
                        )
                    )
    except UserAlreadyExists:
        pass


async def create_first_superuser():
    """
    Корутина, проверяющая, указаны ли в настройках данные для администратора-суперпользователя.
    При наличии оных, вызывает корутину для создания администратора-суперпользователя.
    """
    if all(
        (
            settings.first_superuser_email,
            settings.first_superuser_password,
            settings.first_superuser_name,
            settings.first_superuser_surname,
        )
    ):
        await create_superuser(
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            name=settings.first_superuser_name,
            surname=settings.first_superuser_surname,
            is_superuser=True,
        )
