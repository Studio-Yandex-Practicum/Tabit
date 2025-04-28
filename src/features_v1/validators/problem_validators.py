from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import (
    company_crud,
    message_feed_crud,
    problem_crud,
)
from src.crud.constants import MAX_NUMBER_PROBLEM
from src.features_v1.constants import (
    ERROR_PROBLEM_NOT_FOUND,
    ERROR_PROBLEM_NUMBER,
    VALID_WRONG_MESSAGE_FEED,
    VALID_WRONG_PROBLEM,
)
from src.features_v1.validators.company_validators import check_user_company
from src.models import CompanyUser


async def check_company_problem(
    user_company_id: int, problem_id: int, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие связанной с проблемой компанией и компанией юзера.

    Параметры:
        user_company_id: значение company_id в объекте пользователя;
        problem_id: path-параметр, соответствующий id запрашиваемой проблемы.
    """
    problem = await problem_crud.get_or_404(session, problem_id)
    company = await company_crud.get_or_404(session, problem.company_id)
    if company.id != user_company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=VALID_WRONG_PROBLEM)


async def check_message_feed_and_problem(
    message_feed_id: int, problem_id: int, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий принадлежность запрошенного треда к запрошенной проблеме.

    Параметры:
        message_feed_id: path-параметр, соответствующий id запрашиваемого треда;
        problem_id: path-параметр, соответствующий id запрашиваемой проблемы.
    """
    message_feed = await message_feed_crud.get_or_404(session, message_feed_id)
    if message_feed.problem_id != problem_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VALID_WRONG_MESSAGE_FEED)


async def get_access_to_feeds(
    user_company_id: int, company_slug: str, problem_id: int, session: AsyncSession
) -> None:
    """
    Комбинация валидаторов check_user_company и check_company_problem.
    Используется для доступа к тредам.
    """
    await check_user_company(user_company_id, company_slug, session)
    await check_company_problem(user_company_id, problem_id, session)


async def check_max_number_problems(session: AsyncSession, user: CompanyUser):
    """Проверит количество проблем, в которых участвует пользователь.

    Назначение:
        Установлен лимит количества проблем, в которых может участвовать пользователь.
    Параметры:
        user: экземпляр модели пользователя.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: если превышен лимит.
    """
    all_open_problem = await problem_crud.get_all_open_problem_from_association_by_user_id(
        session,
        user,
    )
    if len(all_open_problem) >= MAX_NUMBER_PROBLEM:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ERROR_PROBLEM_NUMBER.format(MAX_NUMBER_PROBLEM),
        )


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
