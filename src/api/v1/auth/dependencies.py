from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import Authenticator

from src.api.v1.auth.jwt import jwt_auth_backend
from src.api.v1.auth.managers import get_admin_manager, get_user_manager
from src.api.v1.constants import TextError
from src.tabit_management.models import TabitAdminUser
from src.users.models import UserTabit
from src.users.models.enum import RoleUserTabit
from src.api.v1.auth.jwt import tabit_admin, tabit_users

current_superuser = tabit_admin.current_user(active=True, superuser=True)
"""Зависимость. Проверит, является ли пользователь суперпользователем. Вернет этого пользователя."""

current_admin_tabit = tabit_admin.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь админом сервиса. Вернет этого пользователя."""

current_user = tabit_users.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь авторизированным. Вернет этого пользователя."""


def current_company_admin(
    user: UserTabit = Depends(current_user),
    message: str = TextError.FORBIDDEN_ROLE_ADMIN
) -> UserTabit:
    """
    Зависимость. Проверит, является ли пользователь админом от компании. Вернет этого пользователя.
    """
    # TODO: Не проверялось. В бд хранится название переменной - ADMIN, а не её значение - 'Админ'.
    if not user.role == RoleUserTabit.ADMIN:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=message,
        )
    return user


get_current_admin_token = tabit_admin.current_user_token(active=True)
"""
Зависимость. Проверит, является ли пользователь авторизированным.
Вернет этого пользователя и его токен.
"""

get_current_user_token = tabit_users.current_user_token(active=True)
"""
Зависимость. Проверит, является ли пользователь админом сервиса.
Вернет этого пользователя и его токен.
"""

get_current_admin_refresh_token = tabit_admin.current_user_refresh_token(active=True)
