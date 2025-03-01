import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.crud import user_comment_association_crud
from tests.constants import URL


class TestGetProblemFeed:
    @pytest.mark.asyncio
    async def test_get_multiple_message_feeds(
        self, client: AsyncClient, user_1_company_1_token, ten_message_feeds
    ):
        """Тест для проверки получения списка тредов."""
        response = await client.get(URL.MESSAGE_FEED_URL, headers=user_1_company_1_token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code 200, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == len(ten_message_feeds), (
            f'Длина полученного списка должна быть равна {len(ten_message_feeds)}'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('message_feed_1')
    async def test_get_message_feeds_of_another_company(
        self, client: AsyncClient, user_3_company_2_token
    ):
        """Тест для проверки доступа к тредам сотрудников других компаний"""
        response = await client.get(URL.MESSAGE_FEED_URL, headers=user_3_company_2_token)
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code 403, получен {response.status_code}. '
            'Сотрудники компаний должны иметь доступ только к проблемам, связанными с их компанией'
        )

    @pytest.mark.asyncio
    async def test_get_multiple_comments(
        self, client: AsyncClient, user_1_company_1_token, ten_comments
    ):
        """Тест для проверки получения списка комментариев треда."""

        response = await client.get(URL.COMMENTS_URL, headers=user_1_company_1_token)
        result = response.json()
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code 200, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == len(ten_comments), (
            f'Длина полученного списка должна быть равна {len(ten_comments)}'
        )

    @pytest.mark.asyncio
    async def test_get_feed_comments_of_another_company(
        self, client: AsyncClient, user_3_company_2_token, comment_1
    ):
        """Тест для проверки доступа к комментариям сотрудников других компаний"""
        response = await client.get(URL.COMMENTS_URL, headers=user_3_company_2_token)
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code 403, получен {response.status_code}. '
            'Сотрудники компаний могут просматривать комментарии только тех тредов, которые '
            'связаны с их компанией'
        )

    @pytest.mark.asyncio
    async def test_successful_comment_like(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        user_2_company_1,
        user_2_company_1_token,
        comment_1,
    ):
        """Тест для проверки успешного лайка комментария."""
        old_rating = comment_1.rating
        response = await client.get(URL.LIKE_URL, headers=user_2_company_1_token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code 200, получен {response.status_code}'
        )
        await async_session.refresh(comment_1)
        association_obj = await user_comment_association_crud.get(
            comment_1.id, user_2_company_1.id, async_session
        )
        assert comment_1.rating == old_rating + 1, (
            'Рейтинг комментария должен был увеличиться на 1 (стать равным 1)'
        )
        assert association_obj is not None, (
            'При лайке комментария в ассоциативной таблице должна появиться связанная запись'
        )

    @pytest.mark.asyncio
    async def test_successful_comment_unlike(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        user_2_company_1,
        user_2_company_1_token,
        liked_comment_1,
    ):
        """Тест для проверки успешного анлайка комментария."""
        old_rating = liked_comment_1.rating
        response = await client.get(URL.UNLIKE_URL, headers=user_2_company_1_token)
        print(response.json())
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code 200, получен {response.status_code}'
        )
        await async_session.refresh(liked_comment_1)
        association_obj = await user_comment_association_crud.get(
            liked_comment_1.id, user_2_company_1.id, async_session
        )
        assert liked_comment_1.rating == old_rating - 1, (
            'Рейтинг комментария должен был уменьшиться на 1 (стать равным 0)'
        )
        assert association_obj is None, (
            'При анлайке комментария в ассоциативной таблице должна исчезнуть связанная запись'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_like_by_author(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        user_1_company_1,
        user_1_company_1_token,
        comment_1,
    ):
        """Тест для проверки неуспешного лайка комментария автором."""
        old_rating = comment_1.rating
        response = await client.get(URL.LIKE_URL, headers=user_1_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code 400, получен {response.status_code}'
        )
        await async_session.refresh(comment_1)
        assert comment_1.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном лайке.'
        )
        association_obj = await user_comment_association_crud.get(
            comment_1.id, user_1_company_1.id, async_session
        )
        assert association_obj is None, (
            'При неуспешном лайке не должно создаваться записей в ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_repeated_comment_like(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        user_2_company_1,
        user_2_company_1_token,
        liked_comment_1,
    ):
        """Тест для проверки неуспешного повторного лайка пользователем."""
        old_rating = liked_comment_1.rating
        response = await client.get(URL.LIKE_URL, headers=user_2_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code 400, получен {response.status_code}'
        )
        await async_session.refresh(liked_comment_1)
        assert liked_comment_1.rating == old_rating, (
            'Рейтинг комментария не должен меняться при попытке повторного лайка.'
        )
        association_obj = await user_comment_association_crud.get(
            liked_comment_1.id, user_2_company_1.id, async_session
        )
        assert association_obj is not None, (
            'При попытке повторного лайка не должно создаваться дополнительных записей в '
            'ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_unlike_by_author(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        user_1_company_1,
        user_1_company_1_token,
        liked_comment_1,
    ):
        """Тест для проверки неуспешного анлайка комментария автором."""
        old_rating = liked_comment_1.rating
        response = await client.get(URL.UNLIKE_URL, headers=user_1_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code 400, получен {response.status_code}'
        )
        await async_session.refresh(liked_comment_1)
        assert liked_comment_1.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_unlike_by_user(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        user_2_company_1,
        user_2_company_1_token,
        comment_1,
    ):
        """Тест для проверки неуспешного анлайка комментария пользователем."""
        old_rating = comment_1.rating
        response = await client.get(URL.UNLIKE_URL, headers=user_2_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code 400, получен {response.status_code}'
        )
        await async_session.refresh(comment_1)
        assert comment_1.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('comment_1')
    @pytest.mark.parametrize(
        'url_404',
        [
            '/api/v1/Zorg/problems/99/thread',
            '/api/v1/Zorg/problems/1/99/comments',
            '/api/v1/Zorg/problems/1/1/comments/99/like',
            '/api/v1/Zorg/problems/1/1/comments/99/unlike',
        ],
    )
    async def test_404_urls(self, client: AsyncClient, user_1_company_1_token, url_404):
        response = await client.get(url_404, headers=user_1_company_1_token)
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code 404, получен {response.status_code}'
        )
