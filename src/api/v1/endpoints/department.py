from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    summary='Получить список всех отделов',
    dependencies=[Depends(get_async_session)],
)
async def get_departments(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список всех отделов."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список отделов временно недоступен'}


@router.get(
    '/{department_id}',
    summary='Получить информацию об отделе',
    dependencies=[Depends(get_async_session)],
)
async def get_department(
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации об отделе по его ID."""
    # TODO: Реализовать получение отдела по ID из базы данных
    # TODO: Добавить валидацию существования отдела
    return {'message': f'Информация об отделе с ID {department_id} временно недоступна'}


@router.post(
    '/',
    summary='Создать новый отдел',
    dependencies=[Depends(get_async_session)],
)
async def create_department(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового отдела."""
    # TODO: Реализовать создание отдела в базе данных
    # TODO: Добавить валидацию на уникальность названия
    return {'message': 'Создание отдела временно недоступно'}


@router.patch(
    '/{department_id}',
    summary='Обновить информацию об отделе',
    dependencies=[Depends(get_async_session)],
)
async def update_department(
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных отдела."""
    # TODO: Реализовать обновление данных в базе данных
    # TODO: Добавить валидацию на существование отдела
    return {'message': f'Обновление отдела с ID {department_id} временно недоступно'}


@router.delete(
    '/{department_id}',
    summary='Удалить отдел',
    dependencies=[Depends(get_async_session)],
)
async def delete_department(
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление отдела."""
    # TODO: Реализовать удаление данных из базы данных
    # TODO: Добавить валидацию наличия связанных сотрудников перед удалением
    return {'message': f'Удаление отдела с ID {department_id} временно недоступно'}
