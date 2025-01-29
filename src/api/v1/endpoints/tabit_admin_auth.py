from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    # TODO Уточнить целесообразность ручки
    # summary='',
)
async def get_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список администраторов."""

    return {'message': 'Здесь будет какая-то информация.'}


@router.post(
    '/login',
    summary='Вход в сервис для сотрудника Табит',
)
async def login_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Авторизация администратора на сервисе."""

    return {
        'access_token': 'токен доступа',
        'refresh_token': 'токен обновления',
    }


@router.post(
    '/logout',
    summary='Выход из сервиса для сотрудника Табит',
)
async def logout_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Выход для администратора."""

    return {}


@router.post(
    '/refresh-token',
    summary='Обновить токен',
)
async def refresh_token_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Эндпоинт для обновления токена JWT."""

    return {
        'access_token': 'новый токен доступа',
        'refresh_token': 'новый токен обновления',
    }


@router.post(
    '/resetpassword',
    summary='Сбросить пароль',
)
async def resetpassword_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Сброс пароля администратора."""

    return {'message': 'Пароль изменен'}
