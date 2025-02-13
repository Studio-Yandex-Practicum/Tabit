from http import HTTPStatus

from fastapi import Depends, HTTPException

from src.api.v1.auth.jwt import tabit_admin, tabit_user
from src.api.v1.constants import TextError
from src.users.models import UserTabit
from src.users.models.enum import RoleUserTabit

current_superuser = tabit_admin.current_user(active=True, superuser=True)
"""
Зависимость. Проверит, является ли пользователь суперпользователем. Вернет этого пользователя.
"""

current_admin_tabit = tabit_admin.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь админом сервиса. Вернет этого пользователя."""

current_user_tabit = tabit_user.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь авторизированным. Вернет этого пользователя."""


def current_company_admin(
    user: UserTabit = Depends(current_user_tabit),
    message: str = TextError.FORBIDDEN_ROLE_ADMIN,
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
Зависимость. Проверит, является ли пользователь админом сервиса.
Вернет этого пользователя и его токен.
"""

get_current_user_token = tabit_user.current_user_token(active=True)
"""
Зависимость. Проверит, является ли пользователь авторизированным.
Вернет этого пользователя и его токен.
"""

get_current_admin_refresh_token = tabit_admin.current_user_refresh_token(active=True)
"""
Зависимость. Проверит, ликвиден ли refresh-token администратора сервиса.
Вернет этого пользователя и его токен.
"""

get_current_user_refresh_token = tabit_user.current_user_refresh_token(active=True)
"""
Зависимость. Проверит, ликвиден ли refresh-token пользователя сервиса.
Вернет этого пользователя и его токен.
"""
