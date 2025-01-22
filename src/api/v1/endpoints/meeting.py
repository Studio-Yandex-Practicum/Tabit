from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()

@router.get(
    '/',
    summary='Получить список всех встреч',
    dependencies=[Depends(get_async_session)]
)
async def get_meetings(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список всех встреч."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список встреч временно недоступен'}

@router.get(
    '/{meeting_id}',
    summary='Получить информацию о встрече',
    dependencies=[Depends(get_async_session)]
)
async def get_meetings(
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Получение информации о встрече по его ID."""
    # TODO: Реализовать получение встречи по ID из базы данных
    # TODO: Добавить валидацию существования встречи
    return {
        'message': f'Информация о встрече с ID {meeting_id} временно '
                   f'недоступна'
    }

@router.post(
    '/',
    summary='Создать новую встречу',
    dependencies=[Depends(get_async_session)]
)
async def create_meeting(session: AsyncSession = Depends(get_async_session)):
    """Создание новой встречи."""
    # TODO: Реализовать создание встречи в базе данных
    # TODO: Добавить валидацию на уникальность названия
    return {'message': 'Создание встречи временно недоступно'}

@router.patch(
    '/{meeting_id}',
    summary='Обновить информацию о встрече',
    dependencies=[Depends(get_async_session)]
)
async def update_meeting(
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных встречи."""
    # TODO: Реализовать обновление данных в базе данных
    # TODO: Добавить валидацию на существование встречи
    return {
        'message': f'Обновление встречи с ID {meeting_id} временно недоступно'
    }

@router.delete(
    '/{meeting_id}',
    summary='Удалить встречу',
    dependencies=[Depends(get_async_session)]
)
async def delete_meeting(
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление встречи."""
    # TODO: Реализовать удаление встречи из базы данных
    # TODO: Добавить валидацию на существование встречи
    return {
        'message': f'Удаление встречи с ID {meeting_id} временно недоступно'
    }

