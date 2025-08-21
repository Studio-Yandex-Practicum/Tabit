"""Модуль роутеров для аутентификации модераторов компаний."""

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import (
    current_company_moderator,
    get_current_user_refresh_token,
    get_current_user_token,
)
from src.core.auth.jwt import jwt_auth_backend_user
from src.core.auth.managers import get_user_manager
from src.core.auth.protocol import StrategyT
from src.core.database.db_depends import get_async_session
from src.crud import moderator_crud
from src.features_v1.common.password_forgot_reset import (
    PasswordForgotResetMixin,
)
from src.features_v1.validators import check_user_is_active
from src.models import CompanyUser
from src.schemas import TokenReadSchemas, UserReadSchema

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenReadSchemas,
    summary='Вход модератора компании',
    description='Авторизация модератора компании в системе',
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
) -> JSONResponse:
    """
    Авторизация модераторов компаний.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
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

    # Проверяем, что пользователь является модератором
    from src.models import CompanyUserRole

    if user.role != CompanyUserRole.MODERATOR:
        from http import HTTPStatus

        from fastapi import HTTPException

        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Доступ только для модераторов компаний'
        )

    return await jwt_auth_backend_user.login_with_refresh(strategy, user)  # type: ignore[misc]


@router.post(
    '/logout',
    summary='Выход модератора компании',
    description='Выход модератора компании из системы',
)
async def logout(
    user_token: tuple[models.UP, str] = Depends(get_current_user_token),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
) -> Response:
    """
    Выход из системы модераторов компаний.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        user_and_access_token: получение пользователя и его access-токена через зависимость из
            данных запроса.
        strategy: стратегия получения токена.
    """
    user, token = user_token
    return await jwt_auth_backend_user.logout(strategy, user, token)


@router.post(
    '/refresh-token',
    response_model=TokenReadSchemas,
    summary='Обновление токена модератора компании',
    description='Обновление токенов для модератора компании',
)
async def refresh_token_moderator(
    user_and_refresh_token: tuple[CompanyUser, str] = Depends(get_current_user_refresh_token),
    strategy: StrategyT[models.UP, models.ID] = Depends(jwt_auth_backend_user.get_strategy),
) -> JSONResponse:
    """
    Обновление токенов для модератора компании.
    response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
    В заголовке Authorization принимает refresh-token, возвращает обновленные
    access-token и refresh-token.
    Доступно только модераторам компаний.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
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

    # Проверяем, что пользователь является модератором
    from src.models import CompanyUserRole

    if user.role != CompanyUserRole.MODERATOR:
        from http import HTTPStatus

        from fastapi import HTTPException

        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Доступ только для модераторов компаний'
        )

    return await jwt_auth_backend_user.login_with_refresh(strategy, user)  # type: ignore[misc]


@router.get(
    '/me',
    response_model=UserReadSchema,
    summary='Получить информацию о себе',
    description='Получение информации о текущем модераторе компании',
)
async def get_me_moderator(
    session: AsyncSession = Depends(get_async_session),
    user: CompanyUser = Depends(current_company_moderator),
) -> UserReadSchema:
    """
    Для доступа к своей учетной записи модератора компании.
    Доступно только хозяину учетной записи.

    Параметры декоратора:
        path: присвоен не явно. URL-путь, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
        description: подробное описание.
    Параметры функции:
        session: асинхронная сессия через зависимость.
        user: получение пользователя через зависимости.
    """
    return await moderator_crud.get_or_404(session, user.id)


# Создаем экземпляр миксина для модераторов компаний
moderator_password_forgot_reset = PasswordForgotResetMixin()
moderator_password_forgot_reset.create_password_forgot_reset_routes(
    router,
    crud=moderator_crud,
    current_user_dependency=current_company_moderator,
    user_type_name='модератора',
    prefix='',
)
