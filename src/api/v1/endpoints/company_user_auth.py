from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy

from src.api.v1.auth.dependencies import (
    get_current_user_refresh_token,
    get_current_user_token,
    tabit_user,
)
from src.api.v1.auth.jwt import jwt_auth_backend_user
from src.api.v1.auth.managers import get_user_manager
from src.api.v1.auth.protocol import StrategyT
from src.schemas import TokenReadSchemas
from src.core.constants.endpoints import Description, Summary
from src.api.v1.validator import check_user_is_active
from src.models import TabitAdminUser

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenReadSchemas,
    summary=Summary.COMPANY_USER_AUTH_LOGIN,
    description=Description.COMPANY_USER_AUTH_LOGIN,
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
) -> JSONResponse:
    """
    Авторизация пользователей сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        credentials: данные возвращаемые из формы запроса.
        user_manager: менеджер управления пользователей сервиса, вызывается через зависимости.
        strategy: стратегия получения токена.
    Вернет JSON, пример:
        {
            "access_token": "<зашифрованная строка>",
            "refresh_token": "<зашифрованная строка>",
            "token_type": "bearer"
        }
    """
    user = await user_manager.authenticate(credentials)
    check_user_is_active(user)
    return await jwt_auth_backend_user.login_with_refresh(strategy, user)  # type: ignore[misc]


# Cо стороны backend не реализованны какие либо действия при logout пользователя.
# Идет пустой ответ со статусом 204.
# TODO: Либо упростить (возвращает None, status_code=204), либо добавить логику в backend.
@router.post(
    '/logout',
    summary=Summary.COMPANY_USER_AUTH_LOGOUT,
    description=Description.COMPANY_USER_AUTH_LOGOUT,
)
async def logout(
    user_token: tuple[models.UP, str] = Depends(get_current_user_token),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
) -> Response:
    """
    Выход из системы пользователей сервиса.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_and_access_token: : получение пользователя и его access-токена через зависимость из
            данных запроса.
        strategy: стратегия получения токена.
    """
    user, token = user_token
    return await jwt_auth_backend_user.logout(strategy, user, token)


@router.post(
    '/refresh-token',
    response_model=TokenReadSchemas,
    summary=Summary.COMPANY_USER_AUTH_REFRESH_TOKEN,
    description=Description.COMPANY_USER_AUTH_LOGOUT,
)
async def refresh_token_tabit_admin(
    user_and_refresh_token: tuple[TabitAdminUser, str] = Depends(get_current_user_refresh_token),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
) -> JSONResponse:
    """
    Обновление токенов для пользователя сервиса.
    response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
    В заголовке Authorization принимает refresh-token, возвращает обновленные
    access-token и refresh-token.
    Доступно только пользователям сервиса. (У администраторов сервиса своя конечная точка.)

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_and_refresh_token: получение пользователя и его refresh-токена через зависимость из
            данных запроса.
        strategy: стратегия получения токена.
    Вернет JSON, пример:
        {
            "access_token": "<зашифрованная строка>",
            "refresh_token": "<зашифрованная строка>",
            "token_type": "bearer"
        }
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
