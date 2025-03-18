from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.database.db_depends import get_async_session
from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit


async def get_admin_db(session=Depends(get_async_session)):
    """
    Асинхронный генератор.

    Обеспечивает доступ к БД админам ресурса (Tabit Superuser, Tabit Admin).
    """
    yield SQLAlchemyUserDatabase(session, TabitAdminUser)


async def get_user_db(session=Depends(get_async_session)):
    """
    Асинхронный генератор.

    Обеспечивает доступ к БД пользователям ресурса (Tabit Moderator, Tabit User).
    """
    yield SQLAlchemyUserDatabase(session, UserTabit)
