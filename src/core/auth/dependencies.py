"""
Модуль зависимостей для аутентификации и авторизации пользователей.
"""

from http import HTTPStatus

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.auth.jwt import tabit_admin, tabit_user
from src.core.constants import TextErrorBaseConstants
from src.core.database.db_depends import get_async_session
from src.models import Company, CompanyUser, CompanyUserRole

current_superuser = tabit_admin.current_user(active=True, superuser=True)
"""Зависимость. Проверит, является ли пользователь суперпользователем. Вернет этого пользователя.
"""

current_admin_tabit = tabit_admin.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь админом сервиса. Вернет этого пользователя.
"""

current_user_tabit = tabit_user.current_user(active=True)
"""Зависимость. Проверит, является ли пользователь авторизированным. Вернет этого пользователя.
"""


async def current_company_moderator(
    request: Request,
    user: CompanyUser = Depends(current_user_tabit),
    message: str = TextErrorBaseConstants.FORBIDDEN_ROLE_MODERATOR,
    session: AsyncSession = Depends(get_async_session),
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
    request_company_slug = request.path_params['company_slug']
    result = await session.execute(select(Company).where(Company.id == user.company_id))
    db_company_obj = result.scalars().first()
    if db_company_obj.slug != request_company_slug:
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
