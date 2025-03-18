"""
Модуль содержит зависимости для аутентификации и авторизации пользователей.

Предоставляет функции зависимостей для проверки ролей пользователей и доступа к токенам.
"""

from fastapi import Depends, HTTPException, status

from src.api.v1.auth.jwt import tabit_admin, tabit_user
from src.api.v1.constants import TextError
from src.users.models import UserTabit
from src.users.models.enum import CompanyRole

current_tabit_superuser = tabit_admin.current_user(active=True, superuser=True)
# Зависимость. Проверит, является ли пользователь суперпользователем (Tabit Superuser).
# Вернет этого пользователя.

current_tabit_admin = tabit_admin.current_user(active=True)
# Зависимость. Проверит, является ли пользователь админом сервиса (Tabit Admin).
# Вернет этого пользователя.

current_company_user = tabit_user.current_user(active=True)
# Зависимость. Проверит, является ли пользователь авторизированным (Tabit User).
# Вернет этого пользователя.


def current_company_moderator(
    user: UserTabit = Depends(current_company_user),
    message: str = TextError.FORBIDDEN_ROLE_ADMIN,
) -> UserTabit:
    """
    Зависимость. Проверит, является ли пользователь модератором от компании (Tabit Moderator).

    Вернет этого пользователя.
    """
    # TODO: Не проверялось. В бд хранится название переменной - ADMIN, а не её значение - 'Админ'.
    if not user.role == CompanyRole.MODERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )
    return user


get_current_tabit_admin_token = tabit_admin.current_user_token(active=True)
# Зависимость. Проверит, является ли пользователь админом сервиса (Tabit Superuser, Tabit Admin).
# Вернет этого пользователя и его токен.

get_current_company_user_token = tabit_user.current_user_token(active=True)
# Зависимость. Проверит, является ли пользователь авторизированным (Tabit Moderator, Tabit User).
# Вернет этого пользователя и его токен.

get_current_tabit_admin_refresh_token = tabit_admin.current_user_refresh_token(active=True)
# Зависимость. Проверит, ликвиден ли refresh-token администратора сервиса
# (Tabit Superuser, Tabit Admin).
# Вернет этого пользователя и его токен.

get_current_company_user_refresh_token = tabit_user.current_user_refresh_token(active=True)
# Зависимость. Проверит, ликвиден ли refresh-token пользователя сервиса
# (Tabit Moderator, Tabit User).
# Вернет этого пользователя и его токен.
