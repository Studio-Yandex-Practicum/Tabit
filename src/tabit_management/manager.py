"""
Временная замена admin_user_manager.

Полноценный функционал есть в PR #131 https://github.com/Studio-Yandex-Practicum/Tabit/pull/131
После его мерджа в dev, этот файл нужно будет удалить
"""

from uuid import UUID

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.database.db_depends import get_async_session
from src.tabit_management.models import TabitAdminUser


async def get_admin_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, TabitAdminUser)


class AdminUserManager(UUIDIDMixin, BaseUserManager[TabitAdminUser, UUID]):
    pass


async def get_admin_user_manager(admin_user_db=Depends(get_admin_user_db)):
    yield AdminUserManager(admin_user_db)
