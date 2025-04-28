from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import comment_crud, user_comment_association_crud
from src.crud.constants import (
    VALID_COMMENT_NOT_OWNER,
    VALID_LIKE_OWN_COMMENT,
    VALID_NOT_LIKED_COMMENT,
    VALID_REPEATED_LIKE,
    VALID_WRONG_COMMENT,
)
from src.models import AssociationUserComment, CommentFeed

from .problem_validators import (
    check_message_feed_and_problem,
    get_access_to_feeds,
)


class BaseCommentValidator:
    """
    Базовый класс валидаторов для операций с комментариями.

    Назначение:
        Инкапсулирует часто используемые проверки, связанные с комментариями,
        такими как проверка принадлежности к треду, проверка владельца комментария,
        наличие или отсутствие лайка от пользователя.

    Преимущества:
        - Централизация логики валидации: предотвращает дублирование кода в разных валидаторах.
        - Повышение читаемости и сопровождаемости: вся логика в одном месте.
        - Упрощение тестирования и переиспользования логики валидации.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_comment_or_404(self, comment_id: int) -> CommentFeed:
        comment = await comment_crud.get_or_404(self.session, comment_id)
        return comment

    def ensure_comment_in_feed(self, comment: CommentFeed, message_feed_id: int) -> None:
        if comment.message_id != message_feed_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VALID_WRONG_COMMENT)

    def ensure_not_owner(self, comment: CommentFeed, user_id: int) -> None:
        if comment.owner_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_LIKE_OWN_COMMENT
            )

    def ensure_is_owner(self, comment: CommentFeed, user_id: int) -> None:
        if comment.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=VALID_COMMENT_NOT_OWNER
            )

    async def get_user_like(self, user_id: int, comment_id: int) -> AssociationUserComment | None:
        return await user_comment_association_crud.get(comment_id, user_id, self.session)

    def ensure_like_absent(self, like_obj: AssociationUserComment | None) -> None:
        if like_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_REPEATED_LIKE
            )

    def ensure_like_present(
        self, like_obj: AssociationUserComment | None
    ) -> AssociationUserComment:
        if not like_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=VALID_NOT_LIKED_COMMENT
            )
        return like_obj


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
    validator = BaseCommentValidator(session)
    comment = await validator.get_comment_or_404(comment_id)
    validator.ensure_comment_in_feed(comment, message_feed_id)
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
    validator = BaseCommentValidator(None)
    if like_mode:
        validator.ensure_not_owner(comment, user_id)
    else:
        validator.ensure_is_owner(comment, user_id)
    return comment


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
    validator = BaseCommentValidator(session)
    like_obj = await validator.get_user_like(user_id, comment_id)
    if like_mode:
        validator.ensure_like_absent(like_obj)
        return None
    return validator.ensure_like_present(like_obj)
