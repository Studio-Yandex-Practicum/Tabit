import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.validators.comment_validators import (
    check_comment_and_message_feed,
    check_comment_has_likes_from_user,
    check_comment_owner,
)
from src.models import CommentFeed


@pytest.mark.asyncio
class TestCommentValidators:
    async def test_check_comment_and_message_feed_valid(
        self, async_session: AsyncSession, comment_for_test
    ):
        """
        Проверка успешной валидации принадлежности комментария к треду.
        """
        comment, feed, *_ = await comment_for_test(return_all_objects=True)
        result = await check_comment_and_message_feed(comment.id, feed.id, async_session)
        assert isinstance(result, CommentFeed)
        assert result.id == comment.id
        await async_session.close()

    async def test_check_comment_and_message_feed_invalid(
        self, async_session: AsyncSession, comment_for_test
    ):
        """
        Проверка ошибки при несоответствии комментария и треда.
        """
        comment, *_ = await comment_for_test(return_all_objects=True)
        with pytest.raises(HTTPException) as exc:
            await check_comment_and_message_feed(comment.id, 999999, async_session)
        assert exc.value.status_code == 404
        await async_session.close()

    async def test_check_comment_owner_like_mode_raises(self, comment_for_test):
        """
        Проверка, что автор не может лайкнуть свой комментарий.
        """
        comment = await comment_for_test()
        with pytest.raises(HTTPException) as exc:
            await check_comment_owner(comment, comment.owner_id, like_mode=True)
        assert exc.value.status_code == 400

    async def test_check_comment_owner_edit_mode_raises(self, comment_for_test):
        """
        Проверка, что не-автор не может редактировать комментарий.
        """
        comment = await comment_for_test()
        with pytest.raises(HTTPException) as exc:
            await check_comment_owner(comment, 999999, like_mode=False)
        assert exc.value.status_code == 403

    async def test_check_comment_has_likes_absent_like_raises(
        self, async_session: AsyncSession, comment_for_test
    ):
        """
        Проверка ошибки, если пользователь не лайкал комментарий, а от него ожидается лайк.
        """
        comment = await comment_for_test()
        with pytest.raises(HTTPException) as exc:
            await check_comment_has_likes_from_user(str(uuid.uuid4()), comment.id, async_session)
        assert exc.value.status_code == 400
        await async_session.close()

    async def test_check_comment_has_likes_present_like_raises(
        self, async_session: AsyncSession, comment_for_test
    ):
        """
        Проверка ошибки, если пользователь пытается лайкнуть комментарий повторно.
        """
        comment = await comment_for_test(with_like=True)
        with pytest.raises(HTTPException) as exc:
            await check_comment_has_likes_from_user(
                comment.owner_id, comment.id, async_session, like_mode=True
            )
        assert exc.value.status_code == 400
        await async_session.close()
