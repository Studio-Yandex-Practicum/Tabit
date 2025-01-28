from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/thread',
    summary='Получить список всех тредов по проблеме.',
    dependencies=[Depends(get_async_session)],
)
async def get_all_threads(
    company_slug: str, problem_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Получает список всех тредов по проблеме."""
    return {'message': 'Список тредов пока пуст'}


@router.post(
    '/thread',
    summary='Создать тред по проблеме.',
    dependencies=[Depends(get_async_session)],
)
async def create_problem_thread(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание треда по проблеме."""
    return {'message': 'Создание треда пока недоступно.'}


@router.post(
    '/{thread_id}/comments',
    summary='Создать комментарий в треде.',
    dependencies=[Depends(get_async_session)],
)
async def create_thread_comment(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Создание комментария к треду."""
    return {'message': 'Создание комментария пока недоступно.'}


@router.patch(
    '/{thread_id}/comments/{comment_id}',
    summary='Обновить комментарий в треде.',
    dependencies=[Depends(get_async_session)],
)
async def update_thread_comment(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновление комментария в треде."""
    return {'message': 'Обновление комментария пока недоступно.'}


@router.delete(
    '/{thread_id}/comments/{comment_id}',
    summary='Удалить комментарий в треде.',
    dependencies=[Depends(get_async_session)],
)
async def delete_thread_comment(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаление комментария в треде."""
    return {'message': 'Удаление комментария пока недоступно.'}


@router.post(
    '/{thread_id}/comments/{comment_id}/like',
    summary='Поставить лайк комментарию в треде.',
    dependencies=[Depends(get_async_session)],
)
async def create_comment_like(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Поставить лайк комментарию в треде."""
    return {'message': 'Поставить лайк комментарию в треде пока нельзя.'}
