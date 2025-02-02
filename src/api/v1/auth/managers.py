from typing import Optional, Union
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, InvalidPasswordException, UUIDIDMixin

from src.tabit_management.models import TabitAdminUser
from src.tabit_management.schemas import AdminCreateSchema
from src.users.models import UserTabit
from src.users.schemas import UserCreateSchema
from src.constants import ERROR_INVALID_PASSWORD_LENGTH, MIN_LENGTH_PASSWORD
from src.api.v1.auth.dependencies import get_admin_db, get_user_db
from src.api.v1.auth.jwt import jwt_auth_backend


class AdminManager(UUIDIDMixin, BaseUserManager[TabitAdminUser, UUID]):

    async def validate_password(
        self,
        password: str,
        user: Union[AdminCreateSchema, TabitAdminUser],
    ) -> None:
        """Условия валидации пароля."""
        if len(password) < MIN_LENGTH_PASSWORD:
            raise InvalidPasswordException(reason=ERROR_INVALID_PASSWORD_LENGTH)
        # TODO: Расширить валидацию.

    async def on_after_register(
            self, user: TabitAdminUser, request: Optional[Request] = None
    ):
        """Действия после успешной регистрации пользователя."""
        # TODO: Какие действия нужны после успешной регистрации?
        # Нужны ли действия после обновления? Верификации и тп?


class UserManager(UUIDIDMixin, BaseUserManager[UserTabit, UUID]):

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreateSchema, UserTabit],
    ) -> None:
        """Условия валидации пароля."""
        if len(password) < MIN_LENGTH_PASSWORD:
            raise InvalidPasswordException(reason=ERROR_INVALID_PASSWORD_LENGTH)
        # TODO: Расширить валидацию.

    async def on_after_register(
            self, user: UserTabit, request: Optional[Request] = None
    ):
        """Действия после успешной регистрации пользователя."""
        # TODO: Какие действия нужны после успешной регистрации?
        # Нужны ли действия после обновления? Верификации и тп?


async def get_admin_manager(admin_db=Depends(get_admin_db)):
    """Корутина, возвращающая объект класса AdminManager."""
    yield AdminManager(admin_db)


async def get_user_manager(user_db=Depends(get_user_db)):
    """Корутина, возвращающая объект класса UserManager."""
    yield UserManager(user_db)


tabit_admin = FastAPIUsers[TabitAdminUser, UUID](get_admin_manager, [jwt_auth_backend])
# tabit_admin
tabit_users = FastAPIUsers[UserTabit, UUID](get_user_manager, [jwt_auth_backend])


current_superuser = tabit_admin.current_user(active=True, superuser=True)
# TODO: Создать зависимость для модераторов: сотрудников сервиса с урезанными правами доступа.
current_admin = tabit_users.current_user(active=True, superuser=True)
current_user = tabit_users.current_user(active=True)
