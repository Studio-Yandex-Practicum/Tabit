from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.problems.crud.meeting import meeting_crud
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingUpdateSchema,
    MeetingInDB,
)

router = APIRouter()


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings',
    response_model=list[MeetingInDB],
    response_model_exclude_none=True,
    summary='Получить список всех встреч',
    dependencies=[Depends(get_async_session)],
)
async def meetings(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получение списка всех встреч."""
    # return {'message': 'Список встреч пока пуст'}
    filters = {'problem_id': problem_id}
    return await meeting_crud.get_multi(session, filters=filters)


@router.post(
    '/{company_slug}/problems/{problem_id}/meetings',
    response_model=MeetingInDB,
    response_model_exclude_none=True,
    summary='Создать встречу',
    dependencies=[Depends(get_async_session)],
)
async def create_meeting(
    meeting: MeetingCreateSchema,
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать встречу."""
    # # TODO: Проверить уникальность названия встречи
    # # TODO: Проверить доступность даты встречи?
    # return {'message': 'Создание встречи пока недоступно'}
    return await meeting_crud.create(session, meeting)


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingInDB,
    response_model_exclude_none=True,
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
    # # TODO: Проверить существование компании + проблемы + встречи
    # return {'message': 'Информация о встрече пока недоступна'}
    return await meeting_crud.get_or_404(session, meeting_id)


@router.patch(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingInDB,
    response_model_exclude_none=True,
    summary='Обновить информацию о встрече',
    dependencies=[Depends(get_async_session)],
)
async def update_meeting(
    meeting: MeetingUpdateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление встречи."""
    # # TODO: Проверить существование компании + проблемы + встречи
    # # TODO: Проверить уникальность названия встречи
    # # TODO: Проверить доступность даты встречи?
    # return {'message': 'Обновление встречи пока недоступно'}
    return await meeting_crud.update(session, meeting_id, meeting)


@router.delete(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingInDB,
    response_model_exclude_none=True,
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
    # # TODO: Проверить существование компании + проблемы + встречи
    # return {'message': 'Удаление встречи пока недоступно'}
    return await meeting_crud.remove(session, meeting_id)
