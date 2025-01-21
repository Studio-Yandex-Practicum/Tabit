from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    summary='Получить список всех сотрудников',
    dependencies=[Depends(get_async_session)],
)
async def get_employees(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список всех сотрудников."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список сотрудников временно недоступен'}


@router.get(
    '/{user_id}',
    summary='Получить информацию о сотруднике',
    dependencies=[Depends(get_async_session)],
)
async def get_employee(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о сотруднике по его ID."""
    # TODO: Реализовать получение сотрудника по ID из базы данных
    # TODO: Добавить валидацию существования сотрудника
    return {'message': f'Информация о сотруднике с ID {user_id} временно недоступна'}


@router.post(
    '/',
    summary='Создать нового сотрудника',
    dependencies=[Depends(get_async_session)],
)
async def create_employee(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового сотрудника."""
    # TODO: Реализовать создание сотрудника в базе данных
    # TODO: Добавить валидацию на уникальность email, telegramm и тд
    return {'message': 'Создание сотрудника временно недоступно'}


@router.patch(
    '/{user_id}',
    summary='Частичное обновление информации о сотруднике',
    dependencies=[Depends(get_async_session)],
)
async def update_employee(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Частичное обновление данных сотрудника."""
    # TODO: Реализовать частичное обновление данных сотрудника в базе данных
    # TODO: Добавить валидацию существования сотрудника
    # TODO: Добавить валидацию на уникальность email, telegramm и тд
    return {
        'message': f'Частичное обновление сотрудника с ID {user_id} временно недоступно'
    }


@router.delete(
    '/{user_id}',
    summary='Удалить сотрудника',
    dependencies=[Depends(get_async_session)],
)
async def delete_employee(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление сотрудника."""
    # TODO: Реализовать удаление сотрудника из базы данных
    # TODO: Добавить проверку на наличие связанных записей перед удалением
    return {'message': f'Удаление сотрудника с ID {user_id} временно недоступно'}
