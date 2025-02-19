from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.problems.crud.meeting import meeting_crud
from src.problems.schemas.meeting import (
    MeetingCreateSchema,
    MeetingResponseSchema,
    MeetingUpdateSchema,
)

router = APIRouter()


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings',
    response_model=list[MeetingResponseSchema],
    response_model_exclude_none=True,
    summary='Получить список всех встреч',
    status_code=status.HTTP_200_OK,
)
async def meetings(
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех встреч.

    Назначение:
        Возвращает список всех встреч для указанной проблемы.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Список объектов MeetingResponseSchema.
    """
    filters = {'problem_id': problem_id}
    return await meeting_crud.get_multi(session, filters=filters)


@router.post(
    '/{company_slug}/problems/{problem_id}/meetings',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary='Создать встречу',
    status_code=status.HTTP_201_CREATED,
)
async def create_meeting(
    meeting: MeetingCreateSchema,
    company_slug: str,
    problem_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Создает встречу.

    Назначение:
        Создает новую встречу для указанной проблемы.
    Параметры:
        meeting: Данные для создания встречи.
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект MeetingResponseSchema.
    """
    # TODO: Проверить уникальность названия встречи
    # TODO: Проверить доступность даты встречи?
    meeting_data = meeting.model_dump()
    members = meeting.members or []
    created_meeting = await meeting_crud.create_with_members(
        session=session, meeting_data=meeting_data, members=members
    )
    return created_meeting


@router.get(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary='Получить информацию о встрече',
    status_code=status.HTTP_200_OK,
)
async def get_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию о встрече.

    Назначение:
        Возвращает информацию о конкретной встрече.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект MeetingResponseSchema.
    """

    return await meeting_crud.get_or_404(session, meeting_id)


@router.patch(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    response_model=MeetingResponseSchema,
    response_model_exclude_none=True,
    summary='Обновить информацию о встрече',
    status_code=status.HTTP_200_OK,
)
async def update_meeting(
    meeting: MeetingUpdateSchema,
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновляет информацию о встрече.

    Назначение:
        Обновляет данные конкретной встречи.
    Параметры:
        meeting: Данные для обновления встречи.
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        Объект MeetingResponseSchema.
    """
    # TODO: Проверить уникальность названия встречи
    # TODO: Проверить доступность даты встречи?
    return await meeting_crud.update_meeting(session, meeting_id, meeting.model_dump())


@router.delete(
    '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}',
    summary='Удалить встречу',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_meeting(
    company_slug: str,
    problem_id: int,
    meeting_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаляет встречу.

    Назначение:
        Удаляет конкретную встречу.
    Параметры:
        company_slug: Уникальный идентификатор компании.
        problem_id: Идентификатор проблемы.
        meeting_id: Идентификатор встречи.
        session: Асинхронная сессия SQLAlchemy.
    Возвращаемое значение:
        None.
    """
    # TODO: Проверить существование компании + проблемы + встречи
    await meeting_crud.delete_meeting(session, meeting_id)
