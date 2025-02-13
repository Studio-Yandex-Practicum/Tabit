from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.api.v1.auth.dependencies import get_current_user_token
from src.api.v1.auth.jwt import jwt_auth_backend
from src.api.v1.auth.managers import get_user_manager
from src.database.db_depends import get_async_session

router = APIRouter()


# Временное (или нет) решение по аутентификации обычных пользователей.
# Нужно для тестов эндпоинтов сотурдников компаний. Два эндпоинта - login и logout.
# Login возвращает в кач-ве ответа токен. Дальше токен стоит использовать в Postman,
# запрос передать в форме x-www-form-urlencoded с ключами username и password.
# В кач-ве username используется email.


@router.post(
    '/login',
    summary='Авторизация для сотрудников',
)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend.get_strategy),
):
    """
    Авторизация для сотрудников компаний.
    """
    user = await user_manager.authenticate(credentials)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Неверные учетные данные для входа в систему',
        )
    response = await jwt_auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, response)
    return response


@router.post(
    '/logout',
    summary='Запрос для разлогирования',
)
async def logout(
    user_token: tuple[models.UP, str] = Depends(get_current_user_token),
    strategy: Strategy[models.UP, models.ID] = Depends(jwt_auth_backend.get_strategy),
):
    """
    Выход из системы для сотрудников компаний.
    """
    user, token = user_token
    return await jwt_auth_backend.logout(strategy, user, token)


@router.post('/refresh-token')
async def refresh_token_employee(session: AsyncSession = Depends(get_async_session)):
    """Эндпоинт для обновления токена JWT."""

    return {
        'access_token': 'новый секретный секрет',
        'refresh_token': 'новый засекреченный засекрет',
    }


@router.post(
    '/resetpassword',
)
async def resetpassword_employee(session: AsyncSession = Depends(get_async_session)):
    """Сброс пароля пользователя."""

    return {'message': 'Пароль изменен'}
