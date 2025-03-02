from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.companies.crud import company_crud
from src.problems.constants import (
    VALID_COMMENT_NOT_OWNER,
    VALID_LIKE_OWN_COMMENT,
    VALID_NOT_LIKED_COMMENT,
    VALID_REPEATED_LIKE,
    VALID_WRONG_COMMENT,
    VALID_WRONG_COMPANY,
    VALID_WRONG_MESSAGE_FEED,
    VALID_WRONG_PROBLEM,
)
from src.problems.crud import (
    comment_crud,
    message_feed_crud,
    problem_crud,
    user_comment_association_crud,
)
from src.problems.models import AssociationUserComment, CommentFeed


async def check_user_company(
    user_company_id: int, company_slug: str, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие компании юзера и запрошенной компании.

    Параметры:
        user_company_id: значение company_id в объекте пользователя;
        company_slug: path-параметр, соответствующий slug запрашиваемой компании.
    """

    company = await company_crud.get_or_404(session, user_company_id)
    if company.slug != company_slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=VALID_WRONG_COMPANY)


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
    if problem.company_id != user_company_id:
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


async def check_comment_and_message_feed(
    comment_id: int, message_feed_id: int, session: AsyncSession
):
    """
    Валидатор, проверяющий принадлежность запрошенного комментария к запрошенному треду.

    Параметры:
        comment_id: path-параметр, соответствующий id запрашиваемого комментария;
        message_feed_id: path-параметр, соответствующий id запрашиваемого треда.

    Возвращает объект комментария в случае прохождения проверки.
    """
    comment = await comment_crud.get_or_404(session, comment_id)
    if comment.message_id != message_feed_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VALID_WRONG_COMMENT)
    return comment


async def check_comment_owner(
    comment: CommentFeed, user_id: int, like_mode: bool = False
) -> CommentFeed:
    """
    Валидатор, сверяющий автора комментария и текущего пользователя.
    Работает в двух режимах, в зависимости от параметра like_mode:
        1) True: если текущий пользователь является автором комментария,то выбрасывается
           ошибка HTTP 400. Нужно для проверки возможности лайка комментария.
        2) False: если текущий пользователь не является автором комментария,то выбрасывается
           ошибка HTTP 403. Нужно для проверки возможности редактирования комментариев.

    Параметры:
        comment: объект комментария CommentFeed;
        user_id: UUID пользователя, сделавшего запрос к API;
        like_mode: опциональный параметр, определяет способ применения валидатора.
    """
    if like_mode:
        if comment.owner_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_LIKE_OWN_COMMENT
            )
    else:
        if comment.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=VALID_COMMENT_NOT_OWNER
            )


async def get_access_to_feeds(
    user_company_id: int, company_slug: str, problem_id: int, session: AsyncSession
) -> None:
    """
    Комбинация валидаторов check_user_company и check_company_problem.
    Используется для доступа к тредам.
    """
    await check_user_company(user_company_id, company_slug, session)
    await check_company_problem(user_company_id, problem_id, session)


async def get_access_to_comments(
    user_company_id: int,
    company_slug: str,
    problem_id: int,
    message_feed_id: int,
    session: AsyncSession,
) -> None:
    """
    Комбинация валидаторов check_user_company, check_company_problem и
    check_message_feed_and_problem. Используется для доступа к комментариям.
    """
    await get_access_to_feeds(user_company_id, company_slug, problem_id, session)
    await check_message_feed_and_problem(message_feed_id, problem_id, session)


async def check_comment_has_likes_from_user(
    user_id: int, comment_id: int, session: AsyncSession, like_mode: bool = False
) -> AssociationUserComment | None:
    """
    Валидатор, проверяющий, наличие лайка комментария от активного юзера.
    Работает в двух режимах, в зависимости от параметра like_mode:
        1) True: если запись о лайке обнаружена, то выбрасывается ошибка HTTP 400.
        2) False: если запись о лайке не обнаружена, то выбрасывается ошибка HTTP 400.
           В этом варианте возвращается объект модели AssociationUserComment.

    Параметры:
        user_id: UUID пользователя, сделавшего запрос к API;
        comment_id: path-параметр, соответствующий id запрашиваемого комментария;
        like_mode: опциональный параметр, определяет способ применения валидатора.
    """
    if like_mode:
        if await user_comment_association_crud.get(comment_id, user_id, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_REPEATED_LIKE
            )
    else:
        user_comment_obj = await user_comment_association_crud.get(comment_id, user_id, session)
        if not user_comment_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_NOT_LIKED_COMMENT
            )
        return user_comment_obj
