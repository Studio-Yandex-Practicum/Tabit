"""
Модуль зависимостей для аутентификации и авторизации пользователей.
"""

from http import HTTPStatus

from fastapi import Depends, HTTPException

from src.core.auth.jwt import tabit_admin, tabit_user
from src.core.constants import TextErrorBaseConstants
from src.models import CompanyUser, CompanyUserRole

current_superuser = tabit_admin.current_user(active=True, superuser=True)
"""Зависимость. Проверит, является ли пользователь суперпользователем. Вернет этого пользователя.
"""

current_admin_tabit = tabit_admin.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь админом сервиса. Вернет этого пользователя.
"""

current_user_tabit = tabit_user.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь авторизированным. Вернет этого пользователя.
"""


def current_company_moderator(
    user: CompanyUser = Depends(current_user_tabit),
    message: str = TextErrorBaseConstants.FORBIDDEN_ROLE_MODERATOR,
) -> CompanyUser:
    """
    Зависимость. Проверит, является ли пользователь модератором от компании.
    Вернет этого пользователя.
    """
    if not user.role == CompanyUserRole.MODERATOR:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=message,
        )
    return user


get_current_admin_token = tabit_admin.current_user_token(active=True)
"""Зависимость. Проверит, является ли пользователь админом сервиса.
Вернет этого пользователя и его токен.
"""

get_current_user_token = tabit_user.current_user_token(active=True)
"""Зависимость. Проверит, является ли пользователь авторизированным.
Вернет этого пользователя и его токен.
"""

get_current_admin_refresh_token = tabit_admin.current_user_refresh_token(active=True)
"""Зависимость. Проверит, ликвиден ли refresh-token администратора сервиса.
Вернет этого пользователя и его токен.
"""

get_current_user_refresh_token = tabit_user.current_user_refresh_token(active=True)
"""Зависимость. Проверит, ликвиден ли refresh-token пользователя сервиса.
Вернет этого пользователя и его токен.
"""
