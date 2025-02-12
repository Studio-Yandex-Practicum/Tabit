from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_user
from src.database.db_depends import get_async_session
from src.problems.crud import message_feed_crud
from src.problems.schemas.comments import CommentRead
from src.problems.schemas.message_feed import MessageFeedRead
from src.problems.validators import (
    check_company_problem,
    check_user_company,
)
from src.users.models.models import UserTabit

router = APIRouter()


@router.get(
    '/thread',
    summary='Получить список всех тредов по проблеме.',
    response_model=list[MessageFeedRead],
)
async def get_all_threads(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
):
    """Получает список всех тредов по проблеме."""
    await check_user_company(user.company_id, company_slug, session)
    await check_company_problem(user.company_id, problem_id, session)
    await message_feed_crud.get_multi()
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


@router.get(
    '/{thread_id}/comments',
    summary='Получить все комментарии треда.',
    response_model=list[CommentRead],
    dependencies=[Depends(current_user)],
)
async def get_thread_comments(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получить все комментарии в треде."""
    pass


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
