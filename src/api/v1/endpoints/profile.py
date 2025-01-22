from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()

@router.get(
    '/',
    summary='Получить профиль',
    dependencies=[Depends(get_async_session)],
)
async def get_profile(session: AsyncSession = Depends(get_async_session)):
    """Возвращает информацию о пользователе."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Информация о пользователе временно недоступна'}

@router.post(
    '/',
    summary='Создать профиль',
    dependencies=[Depends(get_async_session)],
)
async def create_profile(session: AsyncSession = Depends(get_async_session)):
    """Создание профиля."""
    # TODO: Реализовать создание профиля в базе данных
    # TODO: Добавить валидацию на уникальность email
    return {'message': 'Создание профиля временно недоступно'}