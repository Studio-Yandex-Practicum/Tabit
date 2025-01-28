from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    summary='Получить список всех пользователей',
    dependencies=[Depends(get_async_session)],
)
async def get_users(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список всех пользователей."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список пользователей временно недоступен'}


@router.get(
    '/{user_id}',
    summary='Получить информацию о пользователе',
    dependencies=[Depends(get_async_session)],
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о пользователе по его ID."""
    # TODO: Реализовать получение пользователя по ID из базы данных
    # TODO: Добавить валидацию существования пользователя
    return {'message': f'Информация о пользователе с ID {user_id} временно недоступна'}


@router.post(
    '/',
    summary='Создать нового пользователя',
    dependencies=[Depends(get_async_session)],
)
async def create_user(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового пользователя."""
    # TODO: Реализовать создание пользователя в базе данных
    # TODO: Добавить валидацию на уникальность email, telegram и т.д.
    return {'message': 'Создание пользователя временно недоступно'}


@router.patch(
    '/{user_id}',
    summary='Частичное обновление информации о пользователе',
    dependencies=[Depends(get_async_session)],
)
async def update_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Частичное обновление данных пользователя."""
    # TODO: Реализовать частичное обновление данных пользователя в базе данных
    # TODO: Добавить валидацию существования пользователя
    # TODO: Добавить валидацию на уникальность email, telegram и т.д.
    return {'message': f'Частичное обновление пользователя с ID {user_id} временно недоступно'}


@router.delete(
    '/{user_id}',
    summary='Удалить пользователя',
    dependencies=[Depends(get_async_session)],
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление пользователя."""
    # TODO: Реализовать удаление пользователя из базы данных
    # TODO: Добавить проверку на наличие связанных записей перед удалением
    return {'message': f'Удаление пользователя с ID {user_id} временно недоступно'}
