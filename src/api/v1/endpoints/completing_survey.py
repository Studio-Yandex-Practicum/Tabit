from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()

@router.get(
    '/',
    summary='Получить список всех опросов',
    dependencies=[Depends(get_async_session)],
)
async def get_surveys(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список всех опросов."""
    # TODO: Реализовать получение данных из базы данных
    return {'message': 'Список опросов временно недоступен'}

@router.get(
    '/{survey_id}',
    summary='Получить опрос',
    dependencies=[Depends(get_async_session)],
)
async def get_survey(
    survey_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение опроса по его ID."""
    # TODO: Реализовать получение опроса по ID из базы данных
    # TODO: Добавить валидацию существования опроса
    return {'message': f'Опрос с ID {survey_id} временно недоступен'}


@router.post(
    '/',
    summary='Создать опрос',
    dependencies=[Depends(get_async_session)],
)
async def create_survey(
    session: AsyncSession = Depends(get_async_session),
):
    """Создание опроса."""
    # TODO: Реализовать создание опроса в базе данных
    # TODO: Добавить валидацию на уникальность названия
    return {'message': 'Создание опроса временно недоступно'}
