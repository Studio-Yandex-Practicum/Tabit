from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import Authenticator

from src.api.v1.auth.jwt import jwt_auth_backend
from src.api.v1.auth.managers import get_admin_manager, get_user_manager
from src.api.v1.constants import TEXT_ERROR_FORBIDDEN_ROLE_ADMIN
from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit
from src.users.models.enum import RoleUserTabit

tabit_admin = FastAPIUsers[TabitAdminUser, UUID](get_admin_manager, [jwt_auth_backend])
tabit_users = FastAPIUsers[UserTabit, UUID](get_user_manager, [jwt_auth_backend])

current_superuser = tabit_admin.current_user(active=True, superuser=True)
"""Зависимость. Проверит является ли пользователь суперпользователем. Вернет этого пользователя."""

current_admin_tabit = tabit_admin.current_user(active=True)
"""Зависимость. Проверит является ли пользователь админом сервиса. Вернет этого пользователя."""

current_user = tabit_users.current_user(active=True)
"""Зависимость. Проверит является ли пользователь сервиса. Вернет этого пользователя."""


def current_company_admin(
    user: UserTabit = Depends(current_user),
    message: str = TEXT_ERROR_FORBIDDEN_ROLE_ADMIN
) -> UserTabit:
    """
    Зависимость. Проверит является ли пользователь админом от компании. Вернет этого пользователя.
    """
    # TODO: Не проверялось. В бд хранится название переменной - ADMIN, а не её значение - 'Админ'.
    if not user.role == RoleUserTabit.ADMIN:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=message,
        )
    return user


authenticator_admin = Authenticator([jwt_auth_backend], get_admin_manager)
authenticator_user = Authenticator([jwt_auth_backend], get_admin_manager)
get_current_admin_token = authenticator_admin.current_user_token(active=True)
get_current_user_token = authenticator_user.current_user_token(active=True)
