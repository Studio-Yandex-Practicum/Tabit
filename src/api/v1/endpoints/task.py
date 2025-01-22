from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()

@router.get(
    '/',
    summary='Получить список всех задач',
    dependencies=[Depends(get_async_session)]
)
async def get_tasks(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список всех задач."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список задач временно недоступен'}

@router.get(
    '/{task_id}',
    summary='Получить информацию о задаче',
    dependencies=[Depends(get_async_session)]
)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о задаче по его ID."""
    # TODO: Реализовать получение задачи по ID из базы данных
    # TODO: Добавить валидацию существования задачи
    return {
        'message': f'Информация о задаче с ID {task_id} временно недоступна'
    }

@router.post(
    '/',
    summary='Создать новую задачу',
    dependencies=[Depends(get_async_session)]
)
async def create_task(session: AsyncSession = Depends(get_async_session)):
    """Создание новой задачи."""
    # TODO: Реализовать создание задачи в базе данных
    # TODO: Добавить валидацию на уникальность названия
    return {'message': 'Создание задачи временно недоступно'}

@router.patch(
    '/{task_id}',
    summary='Обновить информацию о задаче',
    dependencies=[Depends(get_async_session)]
)
async def update_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных задачи."""
    # TODO: Реализовать обновление данных в базе данных
    # TODO: Добавить валидацию на существование задачи
    return {
        'message': f'Обновление задачи с ID {task_id} временно недоступно'
    }

@router.delete(
    '/{task_id}',
    summary='Удалить задачу',
    dependencies=[Depends(get_async_session)]
)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление задачи."""
    # TODO: Реализовать удаление задачи из базы данных
    # TODO: Добавить валидацию на существование задачи
    return {
        'message': f'Удаление задачи с ID {task_id} временно недоступно'
    }
