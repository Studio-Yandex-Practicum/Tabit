from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import meeting_crud, result_meeting_crud
from src.features_v1.constants import (
    ERROR_MEETING_NOT_FOUND,
    VALID_NOT_UNIQUE_RESULT_MEETING,
)
from src.models import CompanyUser


async def check_meeting_exists(meeting_id: int, session: AsyncSession):
    """Проверяет существование встречи по ID.

    Назначение:
        Валидирует, что встреча существует в базе данных по заданному ID.
    Параметры:
        meeting_id: Целое число, представляющее ID встречи для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная встреча, если она существует.
    Исключения:
        HTTPException: Если встреча не найдена.
    """
    try:
        await meeting_crud.get_or_404(session, meeting_id)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEETING_NOT_FOUND)


async def check_result_meeting_unique(meeting_id: int, owner: CompanyUser, session: AsyncSession):
    """Проверяет что один пользователь может создать только один результат встречи.

    Назначение:
        Валидирует, что данный пользователь еще не создавал результат данной встречи.
    Параметры:
        meeting_id: Идентификатор связанной встречи.
        owner_id: Идентификатор создателя результата.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: Если результат данной встречи уже создан пользователем.
    """

    if await result_meeting_crud.get_multi(
        filters={'meeting_id': meeting_id, 'owner_id': owner.id}, session=session
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_NOT_UNIQUE_RESULT_MEETING
        )


async def check_meeting_exists(meeting_id: int, session: AsyncSession):
    """Проверяет существование встречи по ID.

    Назначение:
        Валидирует, что встреча существует в базе данных по заданному ID.
    Параметры:
        meeting_id: Целое число, представляющее ID встречи для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная встреча, если она существует.
    Исключения:
        HTTPException: Если встреча не найдена.
    """
    try:
        await meeting_crud.get_or_404(session, meeting_id)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MEETING_NOT_FOUND)