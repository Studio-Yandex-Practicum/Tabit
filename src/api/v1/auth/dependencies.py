from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from src.database.db_depends import get_async_session
from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit
from src.api.v1.auth.managers import tabit_admin, tabit_users


async def get_admin_db(session=Depends(get_async_session)):
    """Асинхронный генератор. Обеспечивает доступ к БД к админам ресурса."""
    yield SQLAlchemyUserDatabase(session, TabitAdminUser)


async def get_user_db(session=Depends(get_async_session)):
    """Асинхронный генератор. Обеспечивает доступ к БД к пользователям ресурса."""
    yield SQLAlchemyUserDatabase(session, UserTabit)


current_superuser = tabit_admin.current_user(active=True, superuser=True)
# TODO: Создать зависимость для модераторов: сотрудников сервиса с урезанными правами доступа.
current_admin = tabit_users.current_user(active=True, superuser=True)
current_user = tabit_users.current_user(active=True)
