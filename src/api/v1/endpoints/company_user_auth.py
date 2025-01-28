from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

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
)
async def login_employee(session: AsyncSession = Depends(get_async_session)):
    """Авторизация пользователя на сервисе."""

    return {
        'access_token': 'секретный секрет',
        'refresh_token': 'засекреченный засекрет',
    }


@router.post(
    '/logout'
)
async def logout_employee(session: AsyncSession = Depends(get_async_session)):
    """Выход из сервиса пользователя."""

    return {}


@router.post(
    '/refresh-token'
)
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

    return {
        'message': 'Пароль изменен'
    }
