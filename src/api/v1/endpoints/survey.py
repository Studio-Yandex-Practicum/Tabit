from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/',
    summary='Получить список всех опросов',
    dependencies=[Depends(get_async_session)]
)
async def get_surveys(
        session: AsyncSession = Depends(get_async_session)
):
    """Возвращает список всех опросов."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список опросов временно недоступен'}

@router.post(
    '/',
    summary='Создать новый опрос',
    dependencies=[Depends(get_async_session)]
)
async def create_survey(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание нового опроса."""
    # TODO: Реализовать создание опроса в базе данных
    # TODO: Добавить валидацию на уникальность названия
    return {'message': 'Создание опроса временно недоступно'}

@router.patch(
    '/{survey_id}',
    summary='Обновить информацию об опросе',
    dependencies=[Depends(get_async_session)]
)
async def update_survey(
    survey_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных опроса."""
    # TODO: Реализовать обновление данных в базе данных
    # TODO: Добавить валидацию на существование опроса
    return {
        'message': f'Обновление опроса с ID {survey_id} временно недоступно'
    }


@router.delete(
    '/{survey_id}',
    summary='Удалить опрос',
    dependencies=[Depends(get_async_session)]
)
async def delete_survey(
    survey_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление опроса."""
    # TODO: Реализовать удаление данных из базы данных
    # TODO: Добавить валидацию наличия связанных записей перед удалением
    return {'message': f'Удаление опроса с ID {survey_id} временно недоступно'}
