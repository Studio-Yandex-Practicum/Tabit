"""Модуль зависимостей для аутентификации и авторизации пользователей."""

from http import HTTPStatus

from fastapi import Depends, HTTPException

from src.core.auth.jwt import tabit_admin, tabit_user
from src.core.constants import TextError
from src.models import CompanyUser, RoleCompanyUser

# Зависимость. Проверит, является ли пользователь суперпользователем. Вернет этого пользователя.
current_superuser = tabit_admin.current_user(active=True, superuser=True)

# Зависимость. Проверит, является ли пользователь админом сервиса. Вернет этого пользователя.
current_admin_tabit = tabit_admin.current_user(active=True)

# Зависимость. Проверит, является ли пользователь авторизированным. Вернет этого пользователя.
current_user_tabit = tabit_user.current_user(active=True)


def current_company_admin(
    user: CompanyUser = Depends(current_user_tabit),
    message: str = TextError.FORBIDDEN_ROLE_ADMIN,
) -> CompanyUser:
    """
    Зависимость. Проверит, является ли пользователь админом от компании. Вернет этого пользователя.
    """
    # TODO: Не проверялось. В бд хранится название переменной - MODERATOR,
    # а не её значение - 'Модератор'.
    if not user.role == RoleCompanyUser.MODERATOR:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=message,
        )
    return user


# Зависимость. Проверит, является ли пользователь админом сервиса.
# Вернет этого пользователя и его токен.
get_current_admin_token = tabit_admin.current_user_token(active=True)

# Зависимость. Проверит, является ли пользователь авторизированным.
# Вернет этого пользователя и его токен.
get_current_user_token = tabit_user.current_user_token(active=True)

# Зависимость. Проверит, ликвиден ли refresh-token администратора сервиса.
# Вернет этого пользователя и его токен.
get_current_admin_refresh_token = tabit_admin.current_user_refresh_token(active=True)

# Зависимость. Проверит, ликвиден ли refresh-token пользователя сервиса.
# Вернет этого пользователя и его токен.
get_current_user_refresh_token = tabit_user.current_user_refresh_token(active=True)
