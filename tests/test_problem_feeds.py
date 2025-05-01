import pytest
from fastapi import status

from src.models import AssociationUserComment
from tests.constants import ProblemFeedsDataConstants, UrlConstants
from tests.utils import get_association_objects_iterator


@pytest.mark.asyncio(loop_scope='session')
class TestGetProblemFeed:
    """Класс для тестов GET-эндпоинтов problem_feeds.py"""

    async def test_get_multiple_message_feeds(
        self, client, get_token_for_user, message_feed_for_test
    ):
        """Тест для проверки получения списка тредов."""
        message_feed, problem, employee, company = await message_feed_for_test(
            return_all_objects=True
        )

        message_feeds = [message_feed]
        message_feeds.extend(
            [
                await message_feed_for_test({'problem_id': problem.id, 'owner_id': employee.id})
                for _ in range(10)
            ]
        )

        token = await get_token_for_user(employee)
        response = await client.get(
            UrlConstants.MESSAGE_FEED_URL.format(company_slug=company.slug, problem_id=problem.id),
            headers=token,
        )

        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )

        result = response.json()
        assert isinstance(result, list)
        assert len(result) == len(message_feeds), (
            f'Длина полученного списка должна быть равна {len(message_feeds)}'
        )

    async def test_get_message_feeds_of_another_company(
        self, client, employee_of_company, get_token_for_user, message_feed_for_test
    ):
        """Тест для проверки доступа к тредам сотрудников других компаний"""
        message_feed, _, _, company = await message_feed_for_test(return_all_objects=True)

        another_user_token = await get_token_for_user(await employee_of_company())
        response = await client.get(
            UrlConstants.MESSAGE_FEED_URL.format(
                company_slug=company.slug, problem_id=message_feed.problem_id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}. '
            'Сотрудники компаний должны иметь доступ только к проблемам, связанными с их компанией'
        )

    async def test_get_multiple_comments(self, client, get_token_for_user, comment_for_test):
        """Тест для проверки получения списка комментариев треда."""
        comment, message_feed, _, employee, company = await comment_for_test(
            return_all_objects=True
        )

        token = await get_token_for_user(employee)

        comments = [comment]
        comments.extend(
            [
                await comment_for_test({'owner_id': employee.id, 'message_id': message_feed.id})
                for _ in range(9)
            ]
        )

        response = await client.get(
            UrlConstants.COMMENTS_URL.format(
                company_slug=company.slug,
                problem_id=message_feed.problem_id,
                message_feed_id=message_feed.id,
            ),
            headers=token,
        )

        result = response.json()
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )

        assert isinstance(result, list)
        assert len(result) == len(comments), (
            f'Длина полученного списка должна быть равна {len(comments)}'
        )

    async def test_get_feed_comments_of_another_company(
        self, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест для проверки доступа к комментариям сотрудников других компаний"""
        _, message_feed, _, _, company = await comment_for_test(return_all_objects=True)

        another_user_token = await get_token_for_user(await employee_of_company())
        response = await client.get(
            UrlConstants.COMMENTS_URL.format(
                company_slug=company.slug,
                problem_id=message_feed.problem_id,
                message_feed_id=message_feed.id,
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}. '
            'Сотрудники компаний могут просматривать комментарии только тех тредов, которые '
            'связаны с их компанией'
        )

    async def test_404_get_urls(self, client, employee_of_company, get_token_for_user):
        """Тест для проверки запросов к несуществующим объектам."""
        employee, company = await employee_of_company(return_company=True)

        token = await get_token_for_user(employee)
        response = await client.get(
            UrlConstants.MESSAGE_FEED_URL.format(company_slug=company.slug, problem_id=999),
            headers=token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


@pytest.mark.asyncio(loop_scope='session')
class TestPostProblemFeed:
    """Класс для тестов POST-эндпоинтов problem_feeds.py"""

    @pytest.mark.parametrize(
        'payload, expected_result', ProblemFeedsDataConstants.MESSAGE_FEED_CREATE_NEW
    )
    async def test_successful_create_message_feed(
        self, client, get_token_for_user, problem_for_test, payload, expected_result
    ):
        """Тест для проверки успешного создания треда к проблеме."""
        problem, employee, company = await problem_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.post(
            UrlConstants.MESSAGE_FEED_URL.format(company_slug=company.slug, problem_id=problem.id),
            headers=token,
            json=payload,
        )

        assert response.status_code == status.HTTP_201_CREATED, (
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )

        result = response.json()
        assert result['text'] == payload['text'], (
            'Значение поля "text" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['important'] == expected_result, (
            'Значение поля "important" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['owner_id'] == str(employee.id), (
            'Значение поля "owner_id" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['problem_id'] == problem.id, (
            'Значение поля "problem_id" созданного объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.parametrize(
        'payload, expected_result', ProblemFeedsDataConstants.MESSAGE_FEED_CREATE_BAD
    )
    async def test_unsuccessful_create_message_feed(
        self, client, get_token_for_user, problem_for_test, payload, expected_result
    ):
        """Тест для проверки неуспешного создания треда к проблеме."""
        problem, employee, company = await problem_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.post(
            UrlConstants.MESSAGE_FEED_URL.format(company_slug=company.slug, problem_id=problem.id),
            headers=token,
            json=payload,
        )

        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )

    async def test_create_message_feed_with_mismatched_company_slug(
        self, client, employee_of_company, get_token_for_user, problem_for_test
    ):
        """
        Тест для проверки попытки создания треда к проблеме другой компании.
        Передаваемый path-параметр company_slug не соответствует компании пользователя,
        сделавшего запрос.
        """
        problem, _, company = await problem_for_test(return_all_objects=True)

        another_user_token = await get_token_for_user(await employee_of_company())
        response = await client.post(
            UrlConstants.MESSAGE_FEED_URL.format(company_slug=company.slug, problem_id=problem.id),
            headers=another_user_token,
            json=ProblemFeedsDataConstants.MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )

    async def test_create_message_feed_with_problem_from_another_company(
        self, client, get_token_for_user, problem_for_test
    ):
        """
        Тест для проверки попытки создания треда к проблеме другой компании.
        В данном тесте переданный company_slug соответствует компании пользователя,
        сделавшего запрос, но переданный problem_id относится к проблеме другой компании.
        """
        _, employee, company = await problem_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        another_problem = await problem_for_test()
        response = await client.post(
            UrlConstants.MESSAGE_FEED_URL.format(
                company_slug=company.slug, problem_id=another_problem.id
            ),
            headers=token,
            json=ProblemFeedsDataConstants.MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )

    async def test_successful_create_comment(
        self, client, get_token_for_user, message_feed_for_test
    ):
        """Тест для проверки успешного создания комментария к треду."""
        message_feed, _, employee, company = await message_feed_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.post(
            UrlConstants.COMMENTS_URL.format(
                company_slug=company.slug,
                problem_id=message_feed.problem_id,
                message_feed_id=message_feed.id,
            ),
            headers=token,
            json=ProblemFeedsDataConstants.COMMENT_CREATE_NEW,
        )

        assert response.status_code == status.HTTP_201_CREATED, (
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )

        result = response.json()
        assert result['text'] == ProblemFeedsDataConstants.COMMENT_CREATE_NEW['text'], (
            'Значение поля "text" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['rating'] == 0, 'Рейтинг нового комментария должен быть равен 0'
        assert result['owner_id'] == str(employee.id), (
            'Значение поля "owner_id" созданного объекта не соответствует ожидаемому значению.'
        )
        assert result['message_id'] == message_feed.id, (
            'Значение поля "message_id" созданного объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.parametrize(
        'payload, expected_result', ProblemFeedsDataConstants.COMMENT_CREATE_BAD
    )
    async def test_unsuccessful_create_comment(
        self, client, get_token_for_user, message_feed_for_test, payload, expected_result
    ):
        """Тест для проверки неуспешного создания комментария к треду."""
        message_feed, _, employee, company = await message_feed_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.post(
            UrlConstants.COMMENTS_URL.format(
                company_slug=company.slug,
                problem_id=message_feed.problem_id,
                message_feed_id=message_feed.id,
            ),
            headers=token,
            json=payload,
        )

        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )

    async def test_create_comment_for_wrong_message_feed(
        self, client, get_token_for_user, message_feed_for_test
    ):
        """
        Тест для проверки попытки создания комментария к треду, не связанному с запрошенной
        проблемой. Т.е. когда тред, соотвествующий переданному thread_id, не связан с проблемой,
        соответствующей переданному problem_id.
        """
        message_feed, _, employee, company = await message_feed_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        wrong_message_feed = await message_feed_for_test()
        response = await client.post(
            UrlConstants.COMMENTS_URL.format(
                company_slug=company.slug,
                problem_id=message_feed.problem_id,
                message_feed_id=wrong_message_feed.id,
            ),
            headers=token,
            json=ProblemFeedsDataConstants.COMMENT_CREATE_NEW,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )

    async def test_successful_comment_like(
        self, async_session, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест для проверки успешного лайка комментария."""
        comment, _, _, _, company = await comment_for_test(return_all_objects=True)

        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        response = await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )

        comment = await async_session.merge(comment)
        await async_session.refresh(comment)
        association_obj = await get_association_objects_iterator(
            async_session, AssociationUserComment, another_user.id, comment.id
        )
        assert comment.rating == 1, (
            'Рейтинг комментария должен был увеличиться на 1 (стать равным 1)'
        )
        assert association_obj.scalar_one_or_none() is not None, (
            'При лайке комментария в ассоциативной таблице должна появиться связанная запись'
        )

    async def test_successful_comment_unlike(
        self, async_session, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест для проверки успешного анлайка комментария."""
        comment, _, _, _, company = await comment_for_test(return_all_objects=True)

        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        comment = await async_session.merge(comment)
        old_rating = comment.rating
        response = await client.post(
            UrlConstants.UNLIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )

        comment = await async_session.merge(comment)
        await async_session.refresh(comment)
        assert comment.rating == old_rating - 1, (
            'Рейтинг комментария должен был уменьшиться на 1 (стать равным 0)'
        )

    async def test_unsuccessful_comment_like_by_author(
        self, client, get_token_for_user, comment_for_test
    ):
        """Тест для проверки неуспешного лайка комментария автором."""
        comment, _, _, employee, company = await comment_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        old_rating = comment.rating
        response = await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=token,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )

        assert comment.rating == old_rating, (
            'Рейтинг комментария не должен меняться при неуспешном лайке.'
        )

    async def test_unsuccessful_repeated_comment_like(
        self, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест для проверки неуспешного повторного лайка пользователем."""
        comment, _, _, _, company = await comment_for_test(return_all_objects=True)

        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        response = await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )

    async def test_unsuccessful_comment_unlike_by_author(
        self, client, get_token_for_user, comment_for_test, employee_of_company
    ):
        """Тест для проверки неуспешного анлайка комментария автором."""
        comment, _, _, employee, company = await comment_for_test(return_all_objects=True)

        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        token = await get_token_for_user(employee)
        response = await client.post(
            UrlConstants.UNLIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=token,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )

    async def test_unsuccessful_comment_unlike_by_user(
        self, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест для проверки неуспешного анлайка комментария пользователем."""
        comment, _, _, _, company = await comment_for_test(return_all_objects=True)

        another_user_token = await get_token_for_user(
            await employee_of_company({'company_id': company.id})
        )
        response = await client.post(
            UrlConstants.UNLIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )

    async def test_comment_like_with_wrong_message_feed_id(
        self,
        client,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """
        Тест для проверки неуспешного лайка существующего комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        _, message_feed, _, _, company = await comment_for_test(return_all_objects=True)

        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        wrong_message_feed = await message_feed_for_test(
            {'problem_id': message_feed.problem_id, 'owner_id': another_user.id}
        )
        response = await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=wrong_message_feed.id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )

    async def test_comment_unlike_with_wrong_message_feed_id(
        self,
        client,
        employee_of_company,
        get_token_for_user,
        message_feed_for_test,
        comment_for_test,
    ):
        """
        Тест для проверки неуспешного анлайка существующего комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        comment, message_feed, _, _, company = await comment_for_test(return_all_objects=True)

        another_user = await employee_of_company({'company_id': company.id})
        another_user_token = await get_token_for_user(another_user)
        await client.post(
            UrlConstants.LIKE_URL.format(
                company_slug=company.slug, message_feed_id=comment.message_id
            ),
            headers=another_user_token,
        )

        wrong_message_feed = await message_feed_for_test(
            {'problem_id': message_feed.problem_id, 'owner_id': another_user.id}
        )
        response = await client.post(
            UrlConstants.UNLIKE_URL.format(
                company_slug=company.slug, message_feed_id=wrong_message_feed.id
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


@pytest.mark.asyncio(loop_scope='session')
class TestPatchProblemFeed:
    """Класс для тестов PATCH-эндпоинтов problem_feeds.py"""

    async def test_successful_patch_comment(self, client, get_token_for_user, comment_for_test):
        """Тест для проверки успешного обновления комментария."""
        comment, _, _, employee, company = await comment_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.patch(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=comment.message_id,
                comment_id=comment.id,
            ),
            headers=token,
            json=ProblemFeedsDataConstants.COMMENT_UPDATE,
        )

        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )

        result = response.json()
        assert result['text'] == ProblemFeedsDataConstants.COMMENT_UPDATE['text'], (
            'Значение поля "text" обновлённого объекта не соответствует ожидаемому значению.'
        )
        assert result['rating'] == comment.rating, (
            'Рейтинг обновлённого комментария должен меняться'
        )
        assert result['owner_id'] == str(comment.owner_id), (
            'Значение поля "owner_id" обновлённого объекта не соответствует ожидаемому значению.'
        )
        assert result['message_id'] == comment.message_id, (
            'Значение поля "message_id" обновлённого объекта не соответствует ожидаемому значению.'
        )

    @pytest.mark.parametrize(
        'payload, expected_result', ProblemFeedsDataConstants.COMMENT_UPDATE_BAD
    )
    async def test_unsuccessful_patch_comment(
        self, client, get_token_for_user, comment_for_test, payload, expected_result
    ):
        """Тест для проверки неуспешного обновления комментария."""
        comment, _, _, employee, company = await comment_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.patch(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=comment.message_id,
                comment_id=comment.id,
            ),
            headers=token,
            json=payload,
        )

        assert response.status_code == expected_result, (
            f'В ответе ожидается status_code {expected_result}, получен {response.status_code}'
        )

    async def test_patch_comment_wrong_owner(
        self, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест для проверки неуспешного обновления комментария другим пользователем."""
        comment, _, _, _, company = await comment_for_test(return_all_objects=True)

        another_user_token = await get_token_for_user(
            await employee_of_company({'company_id': company.id})
        )
        response = await client.patch(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=comment.message_id,
                comment_id=comment.id,
            ),
            headers=another_user_token,
            json=ProblemFeedsDataConstants.COMMENT_UPDATE,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )

    async def test_patch_comment_with_wrong_message_feed_id(
        self, client, get_token_for_user, message_feed_for_test, comment_for_test
    ):
        """
        Тест для проверки неуспешного редактирования комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        comment, message_feed, _, employee, company = await comment_for_test(
            return_all_objects=True
        )

        token = await get_token_for_user(employee)
        wrong_message_feed = await message_feed_for_test(
            {'problem_id': message_feed.problem_id, 'owner_id': employee.id}
        )
        response = await client.patch(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=wrong_message_feed.id,
                comment_id=comment.id,
            ),
            headers=token,
            json=ProblemFeedsDataConstants.COMMENT_UPDATE,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )

    async def test_404_patch_urls(self, client, get_token_for_user, comment_for_test):
        """Тест для проверки редактивроания несуществующего комментария."""
        _, message_feed, problem, employee, company = await comment_for_test(
            return_all_objects=True
        )

        token = await get_token_for_user(employee)
        response = await client.patch(
            UrlConstants.COMMENTS_PATCH_DELETE_404_URL.format(
                company_slug=company.slug,
                problem_id=problem.id,
                message_feed_id=message_feed.id,
                comment_id=99,
            ),
            headers=token,
            json=ProblemFeedsDataConstants.COMMENT_UPDATE,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


@pytest.mark.asyncio(loop_scope='session')
class TestDeleteProblemFeeds:
    """Класс для тестов DELETE-эндпоинтов problem_feeds.py"""

    async def test_successful_delete_comment(self, client, get_token_for_user, comment_for_test):
        """Тест проверки успешного удаления комментария."""
        comment, _, _, employee, company = await comment_for_test(return_all_objects=True)

        token = await get_token_for_user(employee)
        response = await client.delete(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=comment.message_id,
                comment_id=comment.id,
            ),
            headers=token,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'В ответе ожидается status_code {status.HTTP_204_NO_CONTENT}, '
            f'получен {response.status_code}'
        )

    async def test_delete_comment_wrong_owner(
        self, client, employee_of_company, get_token_for_user, comment_for_test
    ):
        """Тест проверки неуспешного удаления комментария не автором."""
        comment, _, _, _, company = await comment_for_test(return_all_objects=True)

        another_user_token = await get_token_for_user(
            await employee_of_company({'company_id': company.id})
        )
        response = await client.delete(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=comment.message_id,
                comment_id=comment.id,
            ),
            headers=another_user_token,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'В ответе ожидается status_code {status.HTTP_403_FORБIDDEN}, '
            f'получен {response.status_code}'
        )

    async def test_delete_comment_with_wrong_message_feed_id(
        self, client, get_token_for_user, message_feed_for_test, comment_for_test
    ):
        """
        Тест для проверки неуспешного удаления комментария, но в запросе передаётся
        некорректный message_feed_id/thread_id.
        """
        comment, message_feed, _, employee, company = await comment_for_test(
            return_all_objects=True
        )

        token = await get_token_for_user(employee)
        wrong_message_feed = await message_feed_for_test(
            {'problem_id': message_feed.problem_id, 'owner_id': employee.id}
        )
        response = await client.delete(
            UrlConstants.COMMENTS_PATCH_DELETE_URL.format(
                company_slug=company.slug,
                message_feed_id=wrong_message_feed.id,
                comment_id=comment.id,
            ),
            headers=token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )

    async def test_404_delete_urls(self, client, get_token_for_user, comment_for_test):
        """Тест для проверки удаления несуществующего комментария."""
        _, message_feed, problem, employee, company = await comment_for_test(
            return_all_objects=True
        )

        token = await get_token_for_user(employee)
        response = await client.delete(
            UrlConstants.COMMENTS_PATCH_DELETE_404_URL.format(
                company_slug=company.slug,
                problem_id=problem.id,
                message_feed_id=message_feed.id,
                comment_id=99,
            ),
            headers=token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
