import re

from fastapi import Depends, HTTPException, Request, status
from fastapi_users import BaseUserManager, UUIDIDMixin, models, schemas

from src.api.v1.auth.access_to_db import get_admin_db, get_user_db
from src.constants import PATTERN_PASSWORD, TEXT_ERROR_INVALID_PASSWORD
from src.tabit_management.models import TabitAdminUser


class BaseTabitUserManager(UUIDIDMixin, BaseUserManager):
    """Базовый менеджер управления пользователями."""

    async def validate_password(
        self,
        password: str,
        user: schemas.UC | models.UP,
    ) -> None:
        """Условия валидации пароля."""
        if re.match(PATTERN_PASSWORD, password) is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TEXT_ERROR_INVALID_PASSWORD,
            )

    async def on_after_register(self, user: TabitAdminUser, request: Request | None = None):
        """Действия после успешной регистрации пользователя."""
        # TODO: Какие действия нужны после успешной регистрации?
        # Нужны ли действия после обновления? Верификации и тп?


class AdminManager(BaseTabitUserManager):
    """
    Менеджер управления пользователями-администраторами сервиса
    (Tabit Superuser, Tabit Admin).
    """


class UserManager(BaseTabitUserManager):
    """Менеджер управления пользователями сервиса от компаний (Tabit Moderator, Tabit User)."""


async def get_admin_manager(admin_db=Depends(get_admin_db)):
    """Корутина, возвращающая объект класса AdminManager."""
    yield AdminManager(admin_db)


async def get_user_manager(user_db=Depends(get_user_db)):
    """Корутина, возвращающая объект класса UserManager."""
    yield UserManager(user_db)
