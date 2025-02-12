from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.crud import company_crud
from src.problems.constants import (
    VALID_WRONG_COMPANY,
    VALID_WRONG_MESSAGE_FEED,
    VALID_WRONG_PROBLEM,
)
from src.problems.crud import message_feed_crud, problem_crud


async def check_user_company(
    user_company_id: int, company_slug: str, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие компании юзера и запрошенной компании.

    user_company_id: значение company_id в объекте пользователя;
    company_slug: path-параметр, соответствующий slug запрашиваемой компании.
    """

    company = await company_crud.get_or_404(session, user_company_id)
    if company.slug != company_slug:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=VALID_WRONG_COMPANY)


async def check_company_problem(
    user_company_id: int, problem_id: int, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие связанной с проблемой компанией и компанией юзера.

    user_company_id: значение company_id в объекте пользователя;
    problem_id: path-параметр, соответствующий id запрашиваемой проблемы.
    """
    problem = await problem_crud.get_with_owner(session, problem_id)
    if problem.owner.company_id != user_company_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=VALID_WRONG_PROBLEM)


async def check_message_feed_and_problem(
    message_feed_id: int, problem_id: int, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий принадлежность запрошенного треда к запрошенной проблеме.

    message_feed_id: path-параметр, соответствующий id запрашиваемого треда.
    problem_id: path-параметр, соответствующий id запрашиваемой проблемы.
    """
    message_feed = await message_feed_crud.get_or_404(session, message_feed_id)
    if message_feed.problem_id != problem_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=VALID_WRONG_MESSAGE_FEED)


async def get_access_to_feeds(
    user_company_id: int, company_slug: str, problem_id: int, session: AsyncSession
) -> None:
    await check_user_company(user_company_id, company_slug, session)
    await check_company_problem(user_company_id, problem_id, session)
