from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin, models, schemas

from src.core.auth.access_to_db import get_admin_db, get_user_db
from src.core.constants.common import ERROR_INVALID_PASSWORD_LENGTH, MIN_LENGTH_PASSWORD
from src.models import TabitAdminUser


class BaseTabitUserManager(UUIDIDMixin, BaseUserManager):
    """Базовый менеджер управления пользователями."""

    async def validate_password(
        self,
        password: str,
        user: schemas.UC | models.UP,
    ) -> None:
        """Условия валидации пароля."""
        if len(password) < MIN_LENGTH_PASSWORD:
            raise InvalidPasswordException(reason=ERROR_INVALID_PASSWORD_LENGTH)
        # TODO: Расширить валидацию.

    async def on_after_register(self, user: TabitAdminUser, request: Request | None = None):
        """Действия после успешной регистрации пользователя."""
        # TODO: Какие действия нужны после успешной регистрации?
        # Нужны ли действия после обновления? Верификации и тп?


class AdminManager(BaseTabitUserManager):
    """Менеджер управления пользователями-администраторами сервиса."""


class UserManager(BaseTabitUserManager):
    """Менеджер управления пользователями сервиса от компаний."""


async def get_admin_manager(admin_db=Depends(get_admin_db)):
    """Корутина, возвращающая объект класса AdminManager."""
    yield AdminManager(admin_db)


async def get_user_manager(user_db=Depends(get_user_db)):
    """Корутина, возвращающая объект класса UserManager."""
    yield UserManager(user_db)
