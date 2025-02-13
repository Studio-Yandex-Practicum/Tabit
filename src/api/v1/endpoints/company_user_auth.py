from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import (
    get_current_user_refresh_token,
    get_current_user_token,
    tabit_user,
)
from src.api.v1.auth.jwt import jwt_auth_backend_user
from src.api.v1.auth.managers import get_user_manager
from src.api.v1.auth.protocol import StrategyT
from src.api.v1.constants import Summary
from src.api.v1.validator import check_user_is_active
from src.database.db_depends import get_async_session
from src.tabit_management.models import TabitAdminUser

router = APIRouter()


@router.get(
    '/',
)
async def get_employees(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список сотрудников."""

    return {
        'employees': [
            'employee_1',
            'employee_2',
            'employee_3',
            '...',
            'employee_n',
        ]
    }


@router.post(
    '/login',
    summary=Summary.COMPANY_USER_AUTH_LOGIN,
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
):
    """
    Авторизация пользователей сервиса.
    """
    user = await user_manager.authenticate(credentials)
    check_user_is_active(user)
    return await jwt_auth_backend_user.login_with_refresh(strategy, user)  # type: ignore[misc]


@router.post(
    '/logout',
    summary=Summary.TABIT_ADMIN_AUTH_LOGOUT,
)
async def logout(
    user_token: tuple[models.UP, str] = Depends(get_current_user_token),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
):
    """
    Выход из системы пользователей сервиса.
    """
    user, token = user_token
    return await jwt_auth_backend_user.logout(strategy, user, token)


@router.post(
    '/refresh-token',
    summary='Обновить токен.',
)
async def refresh_token_tabit_admin(
    user_and_refresh_token: tuple[TabitAdminUser, str] = Depends(get_current_user_refresh_token),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
):
    """
    Обновление токенов для пользователей сервиса.
    В заголовке принимает refresh-token, возвращает обновленные access-token и refresh-token.
    """
    user, _ = user_and_refresh_token
    check_user_is_active(user)
    return await jwt_auth_backend_user.login_with_refresh(strategy, user)  # type: ignore[misc]


# TODO: реализовать нормальное восстановление пароля, если забыл
# TODO: реализовать нормальную замену пароля.
# =====================================================================┐
router.include_router(  # форгот и резет пассворд
    tabit_user.get_reset_password_router(),
    prefix='',
)
# =====================================================================┘
