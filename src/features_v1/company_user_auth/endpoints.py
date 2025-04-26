from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import (
    current_user_tabit,
    get_current_user_refresh_token,
    get_current_user_token,
    tabit_user,
)
from src.core.auth.jwt import jwt_auth_backend_user
from src.core.auth.managers import get_user_manager
from src.core.auth.protocol import StrategyT
from src.core.database.db_depends import get_async_session
from src.crud import user_crud
from src.features_v1.constants import Description, Summary
from src.features_v1.validators import check_telegram_username_for_duplicates, check_user_is_active
from src.models import CompanyUser
from src.schemas import TokenReadSchemas, UserForUserUpdateSchema, UserReadSchema

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenReadSchemas,
    summary=Summary.LOGIN_COMPANY_USER_AUTH,
    description=Description.LOGIN_COMPANY_USER_AUTH,
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
    summary=Summary.LOGOUT_COMPANY_USER_AUTH,
    description=Description.LOGOUT_COMPANY_USER_AUTH,
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
    summary=Summary.REFRESH_TOKEN_COMPANY_USER_AUTH,
    description=Description.REFRESH_TOKEN_COMPANY_USER_AUTH,
)
async def refresh_token_user(
    user_and_refresh_token: tuple[CompanyUser, str] = Depends(get_current_user_refresh_token),
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


@router.get(
    '/me',
    response_model=UserReadSchema,
    summary=Summary.GET_ME_USER_AUTH,
    description=Description.GET_ME_USER_AUTH,
)
async def get_me_user(
    session: AsyncSession = Depends(get_async_session),
    user: CompanyUser = Depends(current_user_tabit),
) -> UserReadSchema:
    """
    Для доступа к своей учетной записи пользователей сервиса.
    Доступно только хозяину учетной записи.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        session: асинхронная сессия через зависимость.
        user: получение пользователя через зависимости.
    """
    return await user_crud.get_or_404(session, user.id)


@router.patch(
    '/me',
    response_model=UserReadSchema,
    summary=Summary.PATCH_ME_USER_AUTH,
    description=Description.PATCH_ME_USER_AUTH,
)
async def update_me_user(
    user_in: UserForUserUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    user: CompanyUser = Depends(current_user_tabit),
) -> UserReadSchema:
    """
    Позволит обновить данные о себе пользователю сервиса.
    Доступно только хозяину учетной записи.

    Параметры декоратора:
        path: присвоен не явно. URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_in: данные переданные в запросе, предварительно подготовленные согласно схеме.
        session: асинхронная сессия через зависимость.
        user: получение пользователя через зависимости.
    """
    await check_telegram_username_for_duplicates(user_in.telegram_username, session)
    return await user_crud.update(session, user, user_in)
