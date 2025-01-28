from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()

@router.get(
    '/{company_slug}/problems/{problem_id}/meetings',
    summary='Получить список всех встреч',
    dependencies=[Depends(get_async_session)],
)
async def meetings(
        company_slug: str,
        problem_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Получение списка всех встреч."""
    return {'message': 'Список встреч пока пуст'}

@router.post(
    '/{company_slug}/problems/{problem_id}/meetings',
    summary='Создать встречу',
    dependencies=[Depends(get_async_session)],
)
async def create_meeting(
        company_slug: str,
        problem_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Создать встречу."""
    # TODO: Проверить уникальность названия встречи
    # TODO: Проверить доступность даты встречи?
    return {'message': 'Создание встречи пока недоступно'}

@router.get(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    summary='Получить информацию о встрече',
    dependencies=[Depends(get_async_session)],
)
async def get_meeting(
        company_slug: str,
        problem_id: int,
        meeting_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о встрече."""
    # TODO: Проверить существование компании + проблемы + встречи
    return {'message': 'Информация о встрече пока недоступна'}

@router.patch(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    summary='Обновить информацию о встрече',
    dependencies=[Depends(get_async_session)],
)
async def update_meeting(
        company_slug: str,
        problem_id: int,
        meeting_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Обновление встречи."""
    # TODO: Проверить существование компании + проблемы + встречи
    # TODO: Проверить уникальность названия встречи
    # TODO: Проверить доступность даты встречи?
    return {'message': 'Обновление встречи пока недоступно'}

@router.delete(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    summary='Удалить встречу',
    dependencies=[Depends(get_async_session)],
)
async def delete_meeting(
        company_slug: str,
        problem_id: int,
        meeting_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Удаление встречи."""
    # TODO: Проверить существование компании + проблемы + встречи
    return {'message': 'Удаление встречи пока недоступно'}
