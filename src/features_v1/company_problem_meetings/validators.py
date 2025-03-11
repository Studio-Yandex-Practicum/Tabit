from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.company_problem_meetings.constants import (
    ERROR_COMPANY_NOT_FOUND,
    ERROR_DATE_MEETING_ALREADY_IN_USE,
    ERROR_MEETING_TITLE_ALREADY_IN_USE,
    ERROR_PROBLEM_NOT_FOUND,
)
from src.features_v1.company_problem_meetings.crud_company import company_crud
from src.features_v1.company_problem_meetings.crud_meeting import meeting_crud
from src.features_v1.company_problem_meetings.crud_problem import problem_crud


# TODO Вместо get_by_company_slug можно использовать метод базового crud
# get_by_slug если исправть как описано в src/companies/crud/company
async def check_company_exists(company_slug: str, session: AsyncSession):
    """Проверяет существование компании по slug.

    Назначение:
        Валидирует, что компания существует в базе данных по заданному slug.
    Параметры:
        company_slug: Строка, представляющая slug компании для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная компания, если она существует.
    Исключения:
        HTTPException: Если компания не найдена.
    """

    if not await company_crud.get_by_company_slug(session, company_slug):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_COMPANY_NOT_FOUND)


async def check_problem_exists(problem_id: int, session: AsyncSession):
    """Проверяет существование проблемы по ID.

    Назначение:
        Валидирует, что проблема существует в базе данных по заданному ID.
    Параметры:
        problem_id: Целое число, представляющее ID проблемы для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная проблема, если она существует.
    Исключения:
        HTTPException: Если проблема не найдена.
    """

    try:
        await problem_crud.get_or_404(session, problem_id)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_PROBLEM_NOT_FOUND)


async def check_meeting_title_unique(title: str, session: AsyncSession):
    """Проверяет уникальность названия встречи.

    Назначение:
        Валидирует, что название встречи уникально и не используется в базе данных.
    Параметры:
        title: Строка, представляющая название встречи для проверки.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: Если название встречи уже используется.
    """

    if not await meeting_crud.get_meeting(title=title, session=session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MEETING_TITLE_ALREADY_IN_USE
        )


async def check_meeting_date_available(date_meeting: str, session: AsyncSession):
    """Проверяет доступность даты встречи.

    Назначение:
        Валидирует, что дата встречи доступна и не конфликтует с существующими встречами.
    Параметры:
        date_meeting: Строка, представляющая дату встречи для проверки.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: Если дата встречи уже занята.
    """

    if not await meeting_crud.get_meeting(date_meeting=date_meeting, session=session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_DATE_MEETING_ALREADY_IN_USE
        )
