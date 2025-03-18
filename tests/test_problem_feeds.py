import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.models import AssociationUserComment, CommentFeed, MessageFeed
from tests.constants import (
    COMMENT_CREATE_BAD,
    COMMENT_CREATE_NEW,
    COMMENT_UPDATE,
    COMMENT_UPDATE_BAD,
    COMPANY_DATA,
    MESSAGE_FEED_CREATE_BAD,
    MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
    MESSAGE_FEED_CREATE_NEW,
    PROBLEM_FEEDS_GET_404,
    URL,
)
from tests.utils import get_association_objects_iterator, get_count, update_object


class TestGetProblemFeed:
    """Класс для тестов GET-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    async def test_get_multiple_message_feeds(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        problem_for_test,
        message_feed_for_test,
    ):
        """Тест для проверки получения списка тредов."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        problem = await problem_for_test(user)
        ten_message_feeds = [
            await message_feed_for_test(user, problem_id=problem.id) for _ in range(10)
        ]
        token = await get_token_for_user(user)
        response = await client.get(
            URL.MESSAGE_FEED_URL.format(problem_id=problem.id), headers=token
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == len(ten_message_feeds), (
            f'Длина полученного списка должна быть равна {len(ten_message_feeds)}'
        )

    @pytest.mark.asyncio
    async def test_get_message_feeds_of_another_company(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
    ):
        """Тест для проверки доступа к тредам сотрудников других компаний"""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        another_user_token = await get_token_for_user(await employee_of_company())
        response = await client.get(
            URL.MESSAGE_FEED_URL.format(problem_id=message_feed.problem_id),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code {status.HTTP_403_FORBIDDEN}, получен {response.status_code}. '
            'Сотрудники компаний должны иметь доступ только к проблемам, связанными с их компанией'
        )

    @pytest.mark.asyncio
    async def test_get_multiple_comments(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """Тест для проверки получения списка комментариев треда."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        token = await get_token_for_user(user)
        ten_comments = [await comment_for_test(user, message_feed=message_feed) for _ in range(10)]
        response = await client.get(
            URL.COMMENTS_URL.format(
                problem_id=message_feed.problem_id, message_feed_id=message_feed.id
            ),
            headers=token,
        )
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
    async def test_get_feed_comments_of_another_company(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """Тест для проверки доступа к комментариям сотрудников других компаний"""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        another_user_token = await get_token_for_user(await employee_of_company())
        await comment_for_test(user, message_feed=message_feed)
        response = await client.get(
            URL.COMMENTS_URL.format(
                problem_id=message_feed.problem_id, message_feed_id=message_feed.id
            ),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code {status.HTTP_403_FORBIDDEN}, получен {response.status_code}. '
            'Сотрудники компаний могут просматривать комментарии только тех тредов, которые '
            'связаны с их компанией'
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'url_404',
        PROBLEM_FEEDS_GET_404,
    )
    async def test_404_get_urls(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        url_404,
    ):
        """Тест для проверки запросов к несуществующим объектам."""
        company = await company_for_test(COMPANY_DATA)
        token = await get_token_for_user(await employee_of_company({'company_id': company.id}))
        response = await client.get(url_404, headers=token)
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
        company_for_test,
        employee_of_company,
        get_token_for_user,
        problem_for_test,
        payload,
        expected_result,
    ):
        """Тест для проверки успешного создания треда к проблеме."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        token = await get_token_for_user(user)
        problem = await problem_for_test(user)
        old_message_feeds_count = await get_count(async_session, MessageFeed)
        response = await client.post(
            URL.MESSAGE_FEED_URL.format(problem_id=problem.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == status.HTTP_201_CREATED, (
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )
        new_message_feeds_count = await get_count(async_session, MessageFeed)
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
        assert result['owner_id'] == str(user.id), (
            'Значение поля "owner_id" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['problem_id'] == problem.id, (
            'Значение поля "problem_id" созданного объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('payload, expected_result', MESSAGE_FEED_CREATE_BAD)
    async def test_unsuccessful_create_message_feed(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        problem_for_test,
        payload,
        expected_result,
    ):
        """Тест для проверки неуспешного создания треда к проблеме."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        token = await get_token_for_user(user)
        problem = await problem_for_test(user)
        old_message_feeds_count = await get_count(async_session, MessageFeed)
        response = await client.post(
            URL.MESSAGE_FEED_URL.format(problem_id=problem.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )
        new_message_feeds_count = await get_count(async_session, MessageFeed)
        assert new_message_feeds_count == old_message_feeds_count, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )

    @pytest.mark.asyncio
    async def test_1_create_message_feed_for_another_company(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        problem_for_test,
    ):
        """
        Тест для проверки попытки создания треда к проблеме другой компании.
        Передаваемый path-параметр company_slug не соответствует компании пользователя,
        сделавшего запрос.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        problem = await problem_for_test(user)
        another_user_token = await get_token_for_user(await employee_of_company())
        old_message_feeds_count = await get_count(async_session, MessageFeed)
        response = await client.post(
            URL.MESSAGE_FEED_URL.format(problem_id=problem.id),
            headers=another_user_token,
            json=MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        new_message_feeds_count = await get_count(async_session, MessageFeed)
        assert new_message_feeds_count == old_message_feeds_count, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )

    @pytest.mark.asyncio
    async def test_2_create_message_feed_for_another_company(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        problem_for_test,
    ):
        """
        Тест для проверки попытки создания треда к проблеме другой компании.
        В данном тесте переданный company_slug соответствует компании пользователя,
        сделавшего запрос, но переданный problem_id относится к проблеме другой компании.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        token = await get_token_for_user(user)
        another_user = await employee_of_company()
        problem = await problem_for_test(another_user)
        old_message_feeds_count = await get_count(async_session, MessageFeed)
        response = await client.post(
            URL.MESSAGE_FEED_URL.format(problem_id=problem.id),
            headers=token,
            json=MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        new_message_feeds_count = await get_count(async_session, MessageFeed)
        assert new_message_feeds_count == old_message_feeds_count, (
            f'Количество объектов MessageFeed должно равняться {old_message_feeds_count}. '
            f'Текущее количество - {new_message_feeds_count}.'
        )

    @pytest.mark.asyncio
    async def test_successful_create_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
    ):
        """Тест для проверки успешного создания комментария к треду."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        token = await get_token_for_user(user)
        message_feed = await message_feed_for_test(user)
        old_comments_count = await get_count(async_session, CommentFeed)
        response = await client.post(
            URL.COMMENTS_URL.format(
                problem_id=message_feed.problem_id, message_feed_id=message_feed.id
            ),
            headers=token,
            json=COMMENT_CREATE_NEW,
        )
        assert response.status_code == status.HTTP_201_CREATED, (
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await get_count(async_session, CommentFeed)
        assert new_comments_count == old_comments_count + 1, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count + 1}. '
            f'Текущее количество - {new_comments_count}.'
        )
        result = response.json()
        assert result['text'] == COMMENT_CREATE_NEW['text'], (
            'Значение поля "text" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['rating'] == 0, 'Рейтинг нового комментария должен быть равен 0'
        assert result['owner_id'] == str(user.id), (
            'Значение поля "owner_id" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['message_id'] == message_feed.id, (
            'Значение поля "message_id" созданного объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('payload, expected_result', COMMENT_CREATE_BAD)
    async def test_unsuccessful_create_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        payload,
        expected_result,
    ):
        """Тест для проверки неуспешного создания комментария к треду."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        token = await get_token_for_user(user)
        message_feed = await message_feed_for_test(user)
        old_comments_count = await get_count(async_session, CommentFeed)
        response = await client.post(
            URL.COMMENTS_URL.format(
                problem_id=message_feed.problem_id, message_feed_id=message_feed.id
            ),
            headers=token,
            json=payload,
        )
        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )
        new_comments_count = await get_count(async_session, CommentFeed)
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    async def test_create_comment_for_wrong_message_feed(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
    ):
        """
        Тест для проверки попытки создания комментария к треду, не связанному с запрошенной
        проблемой. Т.е. когда тред, соотвествующий переданному thread_id, не связан с проблемой,
        соответствующей переданному problem_id.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        token = await get_token_for_user(user)
        message_feed = await message_feed_for_test(user)
        another_user = await employee_of_company()
        wrong_message_feed = await message_feed_for_test(another_user)
        old_comments_count = await get_count(async_session, CommentFeed)
        response = await client.post(
            URL.COMMENTS_URL.format(
                problem_id=message_feed.problem_id, message_feed_id=wrong_message_feed.id
            ),
            headers=token,
            json=COMMENT_CREATE_NEW,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await get_count(async_session, CommentFeed)
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    async def test_successful_comment_like(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест для проверки успешного лайка комментария."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        old_rating = comment.rating
        response = await client.post(
            URL.LIKE_URL.format(message_feed_id=comment.message_id),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        await async_session.refresh(comment)
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, another_user.id, comment.id
        )
        assert comment.rating == old_rating + 1, (
            'Рейтинг комментария должен был увеличиться на 1 (стать равным 1)'
        )
        assert association_obj.scalar_one_or_none() is not None, (
            'При лайке комментария в ассоциативной таблице должна появиться связанная запись'
        )

    @pytest.mark.asyncio
    async def test_successful_comment_unlike(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
        like_a_comment,
    ):
        """Тест для проверки успешного анлайка комментария."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user = await employee_of_company({'company_id': company.id})
        await like_a_comment(another_user, comment)
        another_user_token = await get_token_for_user(another_user)
        old_rating = comment.rating
        response = await client.post(
            URL.UNLIKE_URL.format(message_feed_id=comment.message_id),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        await async_session.refresh(comment)
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, another_user.id, comment.id
        )
        assert comment.rating == old_rating - 1, (
            'Рейтинг комментария должен был уменьшиться на 1 (стать равным 0)'
        )
        assert association_obj.scalar_one_or_none() is None, (
            'При анлайке комментария в ассоциативной таблице должна исчезнуть связанная запись'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_like_by_author(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест для проверки неуспешного лайка комментария автором."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        token = await get_token_for_user(user)
        old_rating = comment.rating
        response = await client.post(
            URL.LIKE_URL.format(message_feed_id=comment.message_id),
            headers=token,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном лайке.'
        )
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, user.id, comment.id
        )
        assert association_obj.scalar_one_or_none() is None, (
            'При неуспешном лайке не должно создаваться записей в ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_repeated_comment_like(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
        like_a_comment,
    ):
        """Тест для проверки неуспешного повторного лайка пользователем."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user = await employee_of_company({'company_id': company.id})
        await like_a_comment(another_user, comment)
        another_user_token = await get_token_for_user(another_user)
        old_rating = comment.rating
        response = await client.post(
            URL.LIKE_URL.format(message_feed_id=comment.message_id),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при попытке повторного лайка.'
        )
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, another_user.id, comment.id
        )
        assert association_obj.scalar_one_or_none() is not None, (
            'При попытке повторного лайка не должно создаваться дополнительных записей в '
            'ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_unlike_by_author(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
        like_a_comment,
    ):
        """Тест для проверки неуспешного анлайка комментария автором."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user = await employee_of_company({'company_id': company.id})
        await like_a_comment(another_user, comment)
        token = await get_token_for_user(user)
        old_rating = comment.rating
        response = await client.post(
            URL.UNLIKE_URL.format(message_feed_id=comment.message_id),
            headers=token,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке'
        )

    @pytest.mark.asyncio
    async def test_unsuccessful_comment_unlike_by_user(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест для проверки неуспешного анлайка комментария пользователем."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user_token = await get_token_for_user(
            await employee_of_company({'company_id': company.id})
        )
        old_rating = comment.rating
        response = await client.post(
            URL.UNLIKE_URL.format(message_feed_id=comment.message_id),
            headers=another_user_token,
        )
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
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """
        Тест для проверки неуспешного лайка существующего комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        comment = await comment_for_test(user)
        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        wrong_message_feed = await message_feed_for_test(
            another_user, problem_id=message_feed.problem_id
        )
        old_rating = comment.rating
        response = await client.post(
            URL.LIKE_URL.format(message_feed_id=wrong_message_feed.id),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном лайке.'
        )
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, another_user.id, comment.id
        )
        assert association_obj.scalar_one_or_none() is None, (
            'При неуспешном лайке не должно создаваться записей в ассоциативной таблице.'
        )

    @pytest.mark.asyncio
    async def test_comment_unlike_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
        like_a_comment,
    ):
        """
        Тест для проверки неуспешного анлайка существующего комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        comment = await comment_for_test(user)
        another_user = await employee_of_company({'company_id': company.id})
        await like_a_comment(another_user, comment)
        another_user_token = await get_token_for_user(another_user)
        wrong_message_feed = await message_feed_for_test(
            another_user, problem_id=message_feed.problem_id
        )
        old_rating = comment.rating
        response = await client.post(
            URL.UNLIKE_URL.format(message_feed_id=wrong_message_feed.id),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        await async_session.refresh(comment)
        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном анлайке.'
        )
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, another_user.id, comment.id
        )
        assert association_obj.scalar_one_or_none() is not None, (
            'При неуспешном анлайке не должна удаляться запись в ассоциативной таблице.'
        )


class TestPatchProblemFeed:
    """Класс для тестов PATCH-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    async def test_successful_patch_comment(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест для проверки успешного обновления комментария."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        token = await get_token_for_user(user)
        old_rating = comment.rating
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=comment.message_id, comment_id=comment.id
            ),
            headers=token,
            json=COMMENT_UPDATE,
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
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
        payload,
        expected_result,
    ):
        """Тест для проверки неуспешного обновления комментария."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        token = await get_token_for_user(user)
        old_comment = jsonable_encoder(comment)
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=comment.message_id, comment_id=comment.id
            ),
            headers=token,
            json=payload,
        )
        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )
        comment = await update_object(async_session, comment)
        assert comment == old_comment, 'Данные обновляемого комментария изменились'

    @pytest.mark.asyncio
    async def test_patch_comment_wrong_owner(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест для проверки неуспешного обновления комментария другим пользователем."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user_token = await get_token_for_user(
            await employee_of_company({'company_id': company.id})
        )
        old_comment = jsonable_encoder(comment)
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=comment.message_id, comment_id=comment.id
            ),
            headers=another_user_token,
            json=COMMENT_UPDATE,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        comment = await update_object(async_session, comment)
        assert comment == old_comment, 'Данные обновляемого комментария изменились'

    @pytest.mark.asyncio
    async def test_patch_comment_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """
        Тест для проверки неуспешного редактирования комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        comment = await comment_for_test(user, message_feed=message_feed)
        token = await get_token_for_user(user)
        wrong_message_feed = await message_feed_for_test(user, problem_id=message_feed.problem_id)
        old_comment = jsonable_encoder(comment)
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=wrong_message_feed.id, comment_id=comment.id
            ),
            headers=token,
            json=COMMENT_UPDATE,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        comment = await update_object(async_session, comment)
        assert comment == old_comment, 'Данные обновляемого комментария изменились'

    @pytest.mark.asyncio
    async def test_404_patch_urls(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
    ):
        """Тест для проверки редактивроания несуществующего комментария."""
        company = await company_for_test(COMPANY_DATA)
        token = await get_token_for_user(await employee_of_company({'company_id': company.id}))
        response = await client.patch(
            URL.COMMENTS_PATCH_DELETE_404_URL,
            headers=token,
            json=COMMENT_UPDATE,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


class TestDeleteProblemFeeds:
    """Класс для тестов DELETE-эндпоинтов problem_feeds.py"""

    @pytest.mark.asyncio
    async def test_successful_delete_comment(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест проверки успешного удаления комментария."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        token = await get_token_for_user(user)
        old_comments_count = await get_count(async_session, CommentFeed)
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=comment.message_id, comment_id=comment.id
            ),
            headers=token,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'В ответе ожидается status_code {status.HTTP_204_NO_CONTENT}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await get_count(async_session, CommentFeed)
        assert new_comments_count == old_comments_count - 1, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count - 1}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    async def test_delete_comment_wrong_owner(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        comment_for_test,
    ):
        """Тест проверки неуспешного удаления комментария не автором."""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        comment = await comment_for_test(user)
        another_user_token = await get_token_for_user(
            await employee_of_company({'company_id': company.id})
        )
        old_comments_count = await get_count(async_session, CommentFeed)
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=comment.message_id, comment_id=comment.id
            ),
            headers=another_user_token,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await get_count(async_session, CommentFeed)
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    async def test_delete_comment_with_wrong_message_feed_id(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """
        Тест для проверки неуспешного удаления комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company({'company_id': company.id})
        message_feed = await message_feed_for_test(user)
        comment = await comment_for_test(user, message_feed=message_feed)
        token = await get_token_for_user(user)
        wrong_message_feed = await message_feed_for_test(user, problem_id=message_feed.problem_id)
        old_comments_count = await get_count(async_session, CommentFeed)
        response = await client.delete(
            URL.COMMENTS_PATCH_DELETE_URL.format(
                message_feed_id=wrong_message_feed.id, comment_id=comment.id
            ),
            headers=token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        new_comments_count = await get_count(async_session, CommentFeed)
        assert new_comments_count == old_comments_count, (
            f'Количество объектов CommentFeed должно равняться {old_comments_count}. '
            f'Текущее количество - {new_comments_count}.'
        )

    @pytest.mark.asyncio
    async def test_404_delete_urls(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
    ):
        """Тест для проверки удаления несуществующего комментария."""
        company = await company_for_test(COMPANY_DATA)
        token = await get_token_for_user(await employee_of_company({'company_id': company.id}))
        response = await client.delete(URL.COMMENTS_PATCH_DELETE_404_URL, headers=token)
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
