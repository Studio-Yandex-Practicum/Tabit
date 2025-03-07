import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.crud import user_comment_association_crud
from src.problems.models import CommentFeed, MessageFeed
from tests.constants import (
    COMMENT_CREATE_BAD,
    COMMENT_CREATE_NEW,
    COMMENT_UPDATE,
    COMMENT_UPDATE_BAD,
    MESSAGE_FEED_CREATE_BAD,
    MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
    MESSAGE_FEED_CREATE_NEW,
    PROBLEM_FEEDS_GET_404,
    URL,
)


class TestGetProblemFeed:
    """Класс для тестов GET-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    async def test_get_multiple_message_feeds(
        self,
        client: AsyncClient,
        employee_1_company_1,
        employee_1_company_1_token,
        problem,
        message_feed_for_test,
    ):
        """Тест для проверки получения списка тредов."""
        ten_message_feeds = [
            await message_feed_for_test(employee_1_company_1, problem_id=problem.id)
            for _ in range(10)
        ]
        response = await client.get(URL.MESSAGE_FEED_URL, headers=employee_1_company_1_token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == len(ten_message_feeds), (
            f'Длина полученного списка должна быть равна {len(ten_message_feeds)}'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('message_feed')
    async def test_get_message_feeds_of_another_company(
        self, client: AsyncClient, employee_3_company_2_token
    ):
        """Тест для проверки доступа к тредам сотрудников других компаний"""
        response = await client.get(URL.MESSAGE_FEED_URL, headers=employee_3_company_2_token)
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code {status.HTTP_403_FORBIDDEN}, получен {response.status_code}. '
            'Сотрудники компаний должны иметь доступ только к проблемам, связанными с их компанией'
        )

    @pytest.mark.asyncio
    async def test_get_multiple_comments(
        self,
        client: AsyncClient,
        employee_1_company_1,
        employee_1_company_1_token,
        message_feed,
        comment_for_test,
    ):
        """Тест для проверки получения списка комментариев треда."""
        ten_comments = [
            await comment_for_test(employee_1_company_1, message_feed=message_feed)
            for _ in range(10)
        ]
        response = await client.get(URL.COMMENTS_URL, headers=employee_1_company_1_token)
        result = response.json()
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == len(ten_comments), (
            f'Длина полученного списка должна быть равна {len(ten_comments)}'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('comment')
    async def test_get_feed_comments_of_another_company(
        self, client: AsyncClient, employee_3_company_2_token
    ):
        """Тест для проверки доступа к комментариям сотрудников других компаний"""
        response = await client.get(URL.COMMENTS_URL, headers=employee_3_company_2_token)
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code {status.HTTP_403_FORBIDDEN}, получен {response.status_code}. '
            'Сотрудники компаний могут просматривать комментарии только тех тредов, которые '
            'связаны с их компанией'
        )

    @pytest.mark.asyncio
    async def test_successful_comment_like(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1,
        employee_2_company_1_token,
        comment,
    ):
        """Тест для проверки успешного лайка комментария."""
        old_rating = comment.rating
        response = await client.get(URL.LIKE_URL, headers=employee_2_company_1_token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        await async_session.refresh(comment)
        association_obj = await user_comment_association_crud.get(
            comment.id, employee_2_company_1.id, async_session
        )
        assert comment.rating == old_rating + 1, (
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
        employee_2_company_1,
        employee_2_company_1_token,
        liked_comment,
    ):
        """Тест для проверки успешного анлайка комментария."""
        old_rating = liked_comment.rating
        response = await client.get(URL.UNLIKE_URL, headers=employee_2_company_1_token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        await async_session.refresh(liked_comment)
        association_obj = await user_comment_association_crud.get(
            liked_comment.id, employee_2_company_1.id, async_session
        )
        assert liked_comment.rating == old_rating - 1, (
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
        employee_1_company_1,
        employee_1_company_1_token,
        comment,
    ):
        """Тест для проверки неуспешного лайка комментария автором."""
        old_rating = comment.rating
        response = await client.get(URL.LIKE_URL, headers=employee_1_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном лайке.'
        )
        association_obj = await user_comment_association_crud.get(
            comment.id, employee_1_company_1.id, async_session
        )
        assert association_obj is None, (
            'При неуспешном лайке не должно создаваться записей в ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_repeated_comment_like(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1,
        employee_2_company_1_token,
        liked_comment,
    ):
        """Тест для проверки неуспешного повторного лайка пользователем."""
        old_rating = liked_comment.rating
        response = await client.get(URL.LIKE_URL, headers=employee_2_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(liked_comment)
        assert liked_comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при попытке повторного лайка.'
        )
        association_obj = await user_comment_association_crud.get(
            liked_comment.id, employee_2_company_1.id, async_session
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
        employee_1_company_1_token,
        liked_comment,
    ):
        """Тест для проверки неуспешного анлайка комментария автором."""
        old_rating = liked_comment.rating
        response = await client.get(URL.UNLIKE_URL, headers=employee_1_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(liked_comment)
        assert liked_comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_unlike_by_user(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1_token,
        comment,
    ):
        """Тест для проверки неуспешного анлайка комментария пользователем."""
        old_rating = comment.rating
        response = await client.get(URL.UNLIKE_URL, headers=employee_2_company_1_token)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке'
        )

    @pytest.mark.asyncio
    async def test_comment_like_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1,
        employee_2_company_1_token,
        message_feed,
        comment,
        message_feed_for_test,
    ):
        """
        Тест для проверки неуспешного лайка существующего комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        await message_feed_for_test(employee_2_company_1, problem_id=message_feed.problem_id)
        old_rating = comment.rating
        response = await client.get(URL.LIKE_BAD_URL, headers=employee_2_company_1_token)
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном лайке.'
        )
        association_obj = await user_comment_association_crud.get(
            comment.id, employee_2_company_1.id, async_session
        )
        assert association_obj is None, (
            'При неуспешном лайке не должно создаваться записей в ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_comment_unlike_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1,
        employee_2_company_1_token,
        message_feed,
        liked_comment,
        message_feed_for_test,
    ):
        """
        Тест для проверки неуспешного анлайка существующего комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        await message_feed_for_test(employee_2_company_1, problem_id=message_feed.problem_id)
        old_rating = liked_comment.rating
        response = await client.get(URL.UNLIKE_BAD_URL, headers=employee_2_company_1_token)
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(liked_comment)
        assert liked_comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке.'
        )
        association_obj = await user_comment_association_crud.get(
            liked_comment.id, employee_2_company_1.id, async_session
        )
        assert association_obj is not None, (
            'При неуспешном анлайке не должна удаляться запись в ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('comment')
    @pytest.mark.parametrize(
        'url_404',
        PROBLEM_FEEDS_GET_404,
    )
    async def test_404_get_urls(self, client: AsyncClient, employee_1_company_1_token, url_404):
        """Тест для проверки запросов к несуществующим объектам."""
        response = await client.get(url_404, headers=employee_1_company_1_token)
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


class TestPostProblemFeed:
    """Класс для тестов POST-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize('payload, expected_result', MESSAGE_FEED_CREATE_NEW)
    async def test_successful_create_message_feed(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1,
        employee_1_company_1_token,
        problem,
        payload,
        expected_result,
    ):
        """Тест для проверки успешного создания треда к проблеме."""
        old_message_feeds_count = await async_session.execute(select(MessageFeed))
        old_message_feeds_count = len(old_message_feeds_count.all())
        response = await client.post(
            URL.MESSAGE_FEED_URL, headers=employee_1_company_1_token, json=payload
        )
        assert response.status_code == status.HTTP_201_CREATED, (
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )
        new_message_feeds_count = await async_session.execute(select(MessageFeed))
        new_message_feeds_count = len(new_message_feeds_count.all())
        assert new_message_feeds_count == old_message_feeds_count + 1, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count + 1}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )
        result = response.json()
        assert result['text'] == payload['text'], (
            'Значение поля "text" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['important'] == expected_result, (
            'Значение поля "important" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['owner_id'] == str(employee_1_company_1.id), (
            'Значение поля "owner_id" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['problem_id'] == problem.id, (
            'Значение поля "problem_id" созданного объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('problem')
    @pytest.mark.parametrize('payload, expected_result', MESSAGE_FEED_CREATE_BAD)
    async def test_unsuccessful_create_message_feed(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1_token,
        payload,
        expected_result,
    ):
        """Тест для проверки неуспешного создания треда к проблеме."""
        old_message_feeds_count = await async_session.execute(select(MessageFeed))
        old_message_feeds_count = len(old_message_feeds_count.all())
        response = await client.post(
            URL.MESSAGE_FEED_URL, headers=employee_1_company_1_token, json=payload
        )
        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )
        new_message_feeds_count = await async_session.execute(select(MessageFeed))
        new_message_feeds_count = len(new_message_feeds_count.all())
        assert new_message_feeds_count == old_message_feeds_count, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('problem')
    async def test_1_create_message_feed_for_another_company(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_3_company_2_token,
    ):
        """
        Тест для проверки попытки создания треда к проблеме другой компании.
        Передаваемый path-параметр company_slug не соответствует компании пользователя,
        сделавшего запрос.
        """
        old_message_feeds_count = await async_session.execute(select(MessageFeed))
        old_message_feeds_count = len(old_message_feeds_count.all())
        response = await client.post(
            URL.MESSAGE_FEED_URL,
            headers=employee_3_company_2_token,
            json=MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        new_message_feeds_count = await async_session.execute(select(MessageFeed))
        new_message_feeds_count = len(new_message_feeds_count.all())
        assert new_message_feeds_count == old_message_feeds_count, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('problem')
    async def test_2_create_message_feed_for_another_company(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1_token,
        employee_3_company_2,
        problem_for_test,
    ):
        """
        Тест для проверки попытки создания треда к проблеме другой компании.
        В данном тесте переданный company_slug соответствует компании пользователя,
        сделавшего запрос, но переданный problem_id относится к проблеме другой компании.
        """
        await problem_for_test(employee_3_company_2, {'name': 'проблема 2'})
        old_message_feeds_count = await async_session.execute(select(MessageFeed))
        old_message_feeds_count = len(old_message_feeds_count.all())
        response = await client.post(
            URL.MESSAGE_FEED_BAD_URL,
            headers=employee_1_company_1_token,
            json=MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        new_message_feeds_count = await async_session.execute(select(MessageFeed))
        new_message_feeds_count = len(new_message_feeds_count.all())
        assert new_message_feeds_count == old_message_feeds_count, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )

    @pytest.mark.asyncio
    async def test_successful_create_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1,
        employee_1_company_1_token,
        message_feed,
    ):
        """Тест для проверки успешного создания комментария к треду."""
        old_comments_count = await async_session.execute(select(CommentFeed))
        old_comments_count = len(old_comments_count.all())
        response = await client.post(
            URL.COMMENTS_URL, headers=employee_1_company_1_token, json=COMMENT_CREATE_NEW
        )
        assert response.status_code == status.HTTP_201_CREATED, (
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await async_session.execute(select(CommentFeed))
        new_comments_count = len(new_comments_count.all())
        assert new_comments_count == old_comments_count + 1, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count + 1}. '
            f'Текущее количество - {new_comments_count}.'
        )
        result = response.json()
        assert result['text'] == COMMENT_CREATE_NEW['text'], (
            'Значение поля "text" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['rating'] == 0, 'Рейтинг нового комментария должен быть равен 0'
        assert result['owner_id'] == str(employee_1_company_1.id), (
            'Значение поля "owner_id" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['message_id'] == message_feed.id, (
            'Значение поля "message_id" созданного объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('message_feed')
    @pytest.mark.parametrize('payload, expected_result', COMMENT_CREATE_BAD)
    async def test_unsuccessful_create_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1_token,
        payload,
        expected_result,
    ):
        """Тест для проверки неуспешного создания комментария к треду."""
        old_comments_count = await async_session.execute(select(CommentFeed))
        old_comments_count = len(old_comments_count.all())
        response = await client.post(
            URL.COMMENTS_URL, headers=employee_1_company_1_token, json=payload
        )
        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )
        new_comments_count = await async_session.execute(select(CommentFeed))
        new_comments_count = len(new_comments_count.all())
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('message_feed')
    async def test_create_comment_for_wrong_message_feed(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1_token,
        employee_3_company_2,
        message_feed_for_test,
    ):
        """
        Тест для проверки попытки создания комментария к треду, не связанному с запрошенной
        проблемой. Т.е. когда тред, соотвествующий переданному thread_id, не связан с проблемой,
        соответствующей переданному problem_id.
        """
        await message_feed_for_test(employee_3_company_2, {'text': 'тред 2'})
        old_comments_count = await async_session.execute(select(CommentFeed))
        old_comments_count = len(old_comments_count.all())
        response = await client.post(
            URL.COMMENTS_WRONG_MESSAGE_FEED_URL,
            headers=employee_1_company_1_token,
            json=COMMENT_CREATE_NEW,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await async_session.execute(select(CommentFeed))
        new_comments_count = len(new_comments_count.all())
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )


class TestPatchProblemFeed:
    """Класс для тестов PATCH-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    async def test_successful_patch_comment(
        self, client: AsyncClient, employee_1_company_1_token, comment
    ):
        """Тест для проверки успешного обновления комментария."""
        old_rating = comment.rating
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL, headers=employee_1_company_1_token, json=COMMENT_UPDATE
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        assert result['text'] == COMMENT_UPDATE['text'], (
            'Значение поля "text" обновлённого объекта не соответствует ожидаемому значению.'
        )
        assert result['rating'] == old_rating, 'Рейтинг обновлённого комментария должен меняться'
        assert result['owner_id'] == str(comment.owner_id), (
            'Значение поля "owner_id" обновлённого объекта не соответствует ожидаемому значению.'
        )
        assert result['message_id'] == comment.message_id, (
            'Значение поля "message_id" обновлённого объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('payload, expected_result', COMMENT_UPDATE_BAD)
    async def test_unsuccessful_patch_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1_token,
        comment,
        payload,
        expected_result,
    ):
        """Тест для проверки неуспешного обновления комментария."""
        old_comment = comment
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL, headers=employee_1_company_1_token, json=payload
        )
        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment == old_comment, 'Данные обновляемого комментария изменились'

    @pytest.mark.asyncio
    async def test_patch_comment_wrong_owner(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1_token,
        comment,
    ):
        """Тест для проверки неуспешного обновления комментария другим пользователем."""
        old_comment = comment
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL, headers=employee_2_company_1_token, json=COMMENT_UPDATE
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment == old_comment, 'Данные обновляемого комментария изменились'

    @pytest.mark.asyncio
    async def test_patch_comment_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1,
        employee_1_company_1_token,
        message_feed,
        comment,
        message_feed_for_test,
    ):
        """
        Тест для проверки неуспешного редактирования комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        await message_feed_for_test(employee_1_company_1, problem_id=message_feed.problem_id)
        old_comment = comment
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_BAD_URL,
            headers=employee_1_company_1_token,
            json=COMMENT_UPDATE,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment == old_comment, 'Данные обновляемого комментария изменились'

    @pytest.mark.asyncio
    async def test_404_patch_urls(self, client: AsyncClient, employee_1_company_1_token):
        """Тест для проверки редактивроания несуществующего комментария."""
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_404_URL,
            headers=employee_1_company_1_token,
            json=COMMENT_UPDATE,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


class TestDeleteProblemFeeds:
    """Класс для тестов DELETE-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('comment')
    async def test_successful_delete_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1_token,
    ):
        """Тест проверки успешного удаления комментария."""
        old_comments_count = await async_session.execute(select(CommentFeed))
        old_comments_count = len(old_comments_count.all())
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_URL, headers=employee_1_company_1_token
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'В ответе ожидается status_code {status.HTTP_204_NO_CONTENT}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await async_session.execute(select(CommentFeed))
        new_comments_count = len(new_comments_count.all())
        assert new_comments_count == old_comments_count - 1, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count - 1}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('comment')
    async def test_delete_comment_wrong_owner(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_2_company_1_token,
    ):
        """Тест проверки неуспешного удаления комментария не автором."""
        old_comments_count = await async_session.execute(select(CommentFeed))
        old_comments_count = len(old_comments_count.all())
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_URL, headers=employee_2_company_1_token
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await async_session.execute(select(CommentFeed))
        new_comments_count = len(new_comments_count.all())
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('comment')
    async def test_delete_comment_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_1_company_1,
        employee_1_company_1_token,
        message_feed,
        message_feed_for_test,
    ):
        """
        Тест для проверки неуспешного удаления комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        await message_feed_for_test(employee_1_company_1, problem_id=message_feed.problem_id)
        old_comments_count = await async_session.execute(select(CommentFeed))
        old_comments_count = len(old_comments_count.all())
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_BAD_URL,
            headers=employee_1_company_1_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await async_session.execute(select(CommentFeed))
        new_comments_count = len(new_comments_count.all())
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    async def test_404_delete_urls(self, client: AsyncClient, employee_1_company_1_token):
        """Тест для проверки удаления несуществующего комментария."""
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_404_URL, headers=employee_1_company_1_token
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
