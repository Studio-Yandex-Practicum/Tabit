from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_user
from src.api.v1.validators import (
    check_comment_owner,
    check_message_feed_and_problem,
    get_access_to_feeds,
)
from src.database.db_depends import get_async_session
from src.problems.crud import comment_crud, message_feed_crud
from src.problems.schemas import (
    CommentCreate,
    CommentRead,
    CommentUpdate,
    FeedsFilterSchema,
    MessageFeedCreate,
    MessageFeedRead,
)
from src.users.models import UserTabit

router = APIRouter()


@router.get(
    '/thread',
    summary='Получить список всех тредов по проблеме.',
    response_model=list[MessageFeedRead],
    status_code=status.HTTP_200_OK,
)
async def get_all_threads(
    company_slug: str,
    problem_id: int,
    query_params: FeedsFilterSchema = Depends(),
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
) -> list[MessageFeedRead]:
    """
    Получает список всех тредов по проблеме.

    Параметры:
        company_slug: path-параметр, слаг компании;
        problem_id: path-параметр, id запрашиваемой проблемы;
        query_params: схема, содержащая данные для ограничения выброки;
        session: асинхронная сессия SQLAlchemy;
        user: объект пользователя, сделавшего запрос к API.
    Доступ только для сотрудников компаний.
    """
    await get_access_to_feeds(user.company_id, company_slug, problem_id, session)
    return await message_feed_crud.get_multi(
        session, query_params.skip, query_params.limit, filters={'problem_id': problem_id}
    )


@router.post(
    '/thread',
    summary='Создать тред по проблеме.',
    response_model=MessageFeedRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_problem_thread(
    company_slug: str,
    problem_id: int,
    create_data: MessageFeedCreate,
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
) -> MessageFeedRead:
    """
    Создание треда по проблеме.
    В качестве ответа возвращается созданный объект MessageFeed.

    Параметры:
        company_slug: path-параметр, слаг компании;
        problem_id: path-параметр, id запрашиваемой проблемы;
        create_data: объект схемы с данными для создания треда
        session: асинхронная сессия SQLAlchemy;
        user: объект пользователя, сделавшего запрос к API.
    Доступ только для сотрудников компаний.
    """
    await get_access_to_feeds(user.company_id, company_slug, problem_id, session)
    return await message_feed_crud.create(session, create_data, problem_id, user.id)


@router.get(
    '/{thread_id}/comments',
    summary='Получить все комментарии треда.',
    response_model=list[CommentRead],
    status_code=status.HTTP_200_OK,
)
async def get_thread_comments(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    query_params: FeedsFilterSchema = Depends(),
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
) -> list[CommentRead]:
    """
    Получить все комментарии треда.

    Параметры:
        company_slug: path-параметр, слаг компании;
        problem_id: path-параметр, id запрашиваемой проблемы;
        thread_id: path-параметр, id запрашиваемого треда;
        query_params: схема, содержащая данные для ограничения выброки;
        session: асинхронная сессия SQLAlchemy;
        user: объект пользователя, сделавшего запрос к API.
    Доступ только для сотрудников компаний.
    """
    await get_access_to_feeds(user.company_id, company_slug, problem_id, session)
    await check_message_feed_and_problem(thread_id, problem_id, session)
    return await comment_crud.get_multi(
        session, query_params.skip, query_params.limit, filters={'message_id': thread_id}
    )


@router.post(
    '/{thread_id}/comments',
    summary='Создать комментарий в треде.',
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_thread_comment(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    create_data: CommentCreate,
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
) -> CommentRead:
    """
    Создание комментария к треду.

    Параметры:
        company_slug: path-параметр, слаг компании;
        problem_id: path-параметр, id запрашиваемой проблемы;
        thread_id: path-параметр, id запрашиваемого треда;
        create_data: объект схемы с данными для создания комментария;
        session: асинхронная сессия SQLAlchemy;
        user: объект пользователя, сделавшего запрос к API.
    Доступ только для сотрудников компаний.
    """
    await get_access_to_feeds(user.company_id, company_slug, problem_id, session)
    await check_message_feed_and_problem(thread_id, problem_id, session)
    return await comment_crud.create(session, create_data, thread_id, user.id)


@router.patch(
    '/{thread_id}/comments/{comment_id}',
    summary='Обновить комментарий в треде.',
    response_model=CommentRead,
    status_code=status.HTTP_200_OK,
)
async def update_thread_comment(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    comment_id: int,
    update_data: CommentUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
) -> CommentRead:
    """
    Обновление комментария в треде.

    Параметры:
        company_slug: path-параметр, слаг компании;
        problem_id: path-параметр, id запрашиваемой проблемы;
        thread_id: path-параметр, id запрашиваемого треда;
        comment_id: paht-параметр, id запрашиваемого комментария;
        update_data: объект схемы с данными для обновления комментария;
        session: асинхронная сессия SQLAlchemy;
        user: объект пользователя, сделавшего запрос к API.
    Доступ только для сотрудников компаний.
    """
    await get_access_to_feeds(user.company_id, company_slug, problem_id, session)
    await check_message_feed_and_problem(thread_id, problem_id, session)
    comment = await check_comment_owner(comment_id, user.id, session)
    return await comment_crud.update(session, comment, update_data)


@router.delete(
    '/{thread_id}/comments/{comment_id}',
    summary='Удалить комментарий в треде.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_thread_comment(
    company_slug: str,
    problem_id: int,
    thread_id: int,
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: UserTabit = Depends(current_user),
) -> None:
    """
    Удаление комментария в треде.

    Параметры:
        company_slug: path-параметр, слаг компании;
        problem_id: path-параметр, id запрашиваемой проблемы;
        thread_id: path-параметр, id запрашиваемого треда;
        comment_id: paht-параметр, id запрашиваемого комментария;
        session: асинхронная сессия SQLAlchemy;
        user: объект пользователя, сделавшего запрос к API.
    Доступ только для сотрудников компаний.
    """
    await get_access_to_feeds(user.company_id, company_slug, problem_id, session)
    await check_message_feed_and_problem(thread_id, problem_id, session)
    comment = await check_comment_owner(comment_id, user.id, session)
    await comment_crud.remove(session, comment)


# TODO: Уточнить, нужна ли реализация данного функционала.
# Если нужна, то, возможно, стоит реализовать и дизлайки? Оба случая решаются добавлением
# одного параметра в модель (rating/likes и т.п.).
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
