import random
import string
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import URL


def generate_meeting_data(problem_id=None, owner_id=None, all_fields=False, members=None):
    """Генерирует реалистичные данные для создания встреч."""

    def random_string(length=10):
        """Генерирует случайную строку указанной длины."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    data = {
        'title': f'Встреча {random_string(5)}',
        'date_meeting': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'place': f'Место встречи {random_string(6)}',
    }
    if all_fields:
        data.update(
            {
                'description': f'Описание встречи {random_string(15)}',
            }
        )
    if members:
        data.update(
            {
                'members': members,
            }
        )
    return data


class TestMeetingsPost:
    """
    Тесты post запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_create_meeting_whth_all_fields(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """
        Тест пост запроса на создание встречи со всеми полями.
        """
        problem, employee, company = await problem_for_test(return_all_objects=True)

        meeting_data = generate_meeting_data(all_fields=True)

        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=meeting_data,
            headers=await get_token_for_user(employee),
        )

        assert response_meeting.status_code == status.HTTP_201_CREATED, response_meeting.json()

        response_data = response_meeting.json()

        assert response_data['description'] == meeting_data['description']
        assert response_data['place'] == meeting_data['place']

    @pytest.mark.asyncio
    async def test_create_meeting_with_required_fields(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """
        Тест пост запроса на создание встречи только с обязательными полями.
        """
        problem, employee, company = await problem_for_test(return_all_objects=True)

        meeting_data = generate_meeting_data()

        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=meeting_data,
            headers=await get_token_for_user(employee),
        )

        assert response_meeting.status_code == status.HTTP_201_CREATED, response_meeting

        response_data = response_meeting.json()

        assert response_data['title'] == meeting_data['title']
        assert response_data['date_meeting'] == meeting_data['date_meeting']

    @pytest.mark.skip(
        'На данном этапе не проводится никаких проверок на уникальность названий встреч.'
    )
    @pytest.mark.asyncio
    async def test_create_meeting_with_unique_name(
        self,
        client: AsyncClient,
        meeting_for_test,
        get_token_for_user,
    ):
        """
        Тест пост запроса на проверку уникальности имени.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        new_date_meeting = (
            datetime.combine(meeting.date_meeting, datetime.min.time()) + timedelta(days=1)
        ).strftime('%Y-%m-%d')

        meeting_data = generate_meeting_data()

        meeting_data['title'] = meeting.title
        meeting_data['date_meeting'] = new_date_meeting

        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=meeting_data,
            headers=await get_token_for_user(employee),
        )

        assert response_meeting.status_code == status.HTTP_400_BAD_REQUEST
        assert response_meeting.json() == {'detail': 'Такое название встречи уже используется'}

    @pytest.mark.skip('На данном этапе не проводится никаких проверок на совпадения дат.')
    @pytest.mark.asyncio
    async def test_create_meeting_with_uncurrent_date(
        self,
        client: AsyncClient,
        meeting_for_test,
        get_token_for_user,
    ):
        """
        Тест пост запроса на создание встречи c не коректной датой.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        new_date_meeting = (datetime.combine(meeting.date_meeting, datetime.min.time())).strftime(
            '%Y-%m-%d'
        )

        meeting_data = generate_meeting_data()
        meeting_data['date_meeting'] = new_date_meeting

        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=meeting_data,
            headers=await get_token_for_user(employee),
        )

        assert response_meeting.status_code == status.HTTP_400_BAD_REQUEST
        assert response_meeting.json() == {'detail': 'Дата встречи уже занята'}

    @pytest.mark.asyncio
    async def test_create_no_company_no_problems(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """
        Тест пост запроса на создание встречи c несуществующей компанией или проблемой.
        """
        problem, employee, company = await problem_for_test(return_all_objects=True)

        variants = (
            (
                problem.id,
                invalid_slug := 'No-way-company',
                status.HTTP_404_NOT_FOUND,
                {'detail': f'Не найден объект Company по данному slug: {invalid_slug}'},
            ),
            (
                problem.id + 1,
                company.slug,
                status.HTTP_404_NOT_FOUND,
                {'detail': f'Не найден объект Problem по данному id: {problem.id + 1}'},
            ),
        )

        for problem_id, company_slug, status_code, detail in variants:  # noqa
            meeting_data = generate_meeting_data()

            response_meeting = await client.post(
                URL.MEETINGS_ENDPOINT.format(company_slug=company_slug, problem_id=problem_id),
                json=meeting_data,
                headers=await get_token_for_user(employee),
            )

            assert response_meeting.status_code == status_code, response_meeting
            assert response_meeting.json() == detail


class TestMeetingsGet:
    """
    Тесты get запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_get_all_meetings_by_problem(
        self, client: AsyncClient, meeting_for_test, get_token_for_user
    ):
        """
        Проверка получения списка встреч по проблеме.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        meetings_data = [meeting]
        meetings_data.extend(
            [
                await meeting_for_test({'problem_id': problem.id, 'owner_id': employee.id})
                for _ in range(3)
            ]
        )

        response = await client.get(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_200_OK, response

        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == len(meetings_data)

    @pytest.mark.asyncio
    async def test_get_single_meeting_info(
        self,
        client: AsyncClient,
        meeting_for_test,
        get_token_for_user,
    ):
        """
        Проверка получения информации о конкретной встрече.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        response = await client.get(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug,
                problem_id=problem.id,
                meeting_id=meeting.id,
            ),
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_200_OK, response

        response_data = response.json()

        assert response_data['id'] == meeting.id
        assert response_data['title'] == meeting.title
        assert response_data['date_meeting'] == meeting.date_meeting.isoformat()
        assert response_data['status'] == meeting.status

    @pytest.mark.asyncio
    async def test_get_meetings_standard_response(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """
        Проверка корректного ответа на стандартный запрос если нет встреч.
        """
        problem, employee, company = await problem_for_test(return_all_objects=True)

        response = await client.get(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_200_OK, response

        response_data = response.json()

        assert isinstance(response_data, list)
        assert len(response_data) == 0


class TestMeetingsUpdate:
    """
    Тесты PATCH запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_patch_meeting_full_update(
        self,
        client: AsyncClient,
        meeting_for_test,
        get_token_for_user,
    ):
        """
        Полное обновление всех полей встречи.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        updated_data = {
            'title': 'Updated Title',
            'date_meeting': (datetime.now() + timedelta(days=10)).date().isoformat(),
            'description': 'Updated Description',
            'status': 'Приостановлена',
            'place': 'Updated Place',
        }

        response = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem.id, meeting_id=meeting.id
            ),
            json=updated_data,
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_200_OK, response

        data = response.json()

        for key, value in updated_data.items():
            assert data[key] == value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'field, value',
        [
            ('title', 'Updated Title'),
            ('description', 'Updated Description'),
            ('date_meeting', (datetime.now() + timedelta(days=10)).date().isoformat()),
            ('status', 'Приостановлена'),
            ('place', 'Updated Place'),
        ],
    )
    async def test_patch_meeting_partial_update(
        self,
        client: AsyncClient,
        meeting_for_test,
        field,
        value,
        get_token_for_user,
    ):
        """
        Обновление каждого поля встречи отдельно.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        response = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem.id, meeting_id=meeting.id
            ),
            json={field: value},
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data[field] == value

    @pytest.mark.asyncio
    async def test_update_meeting_not_found_problem(
        self,
        client: AsyncClient,
        employee_of_company,
        get_token_for_user,
    ):
        """
        Попытка обновить несуществующую проблему.
        """
        employee, company = await employee_of_company(return_company=True)

        problem_id = random.randint(1, 100)
        meeting_id = random.randint(1, 100)

        response_patch = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
            ),
            json={'title': 'No Matter'},
            headers=await get_token_for_user(employee),
        )

        assert response_patch.status_code == status.HTTP_404_NOT_FOUND, response_patch
        assert response_patch.json() == {
            'detail': f'Не найден объект Problem по данному id: {problem_id}'
        }


class TestMeetingsDelete:
    """
    Тесты delete запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_delete_meeting(
        self,
        client: AsyncClient,
        meeting_for_test,
        get_token_for_user,
    ):
        """
        Тест успешного удаления встречи.
        """
        meeting, problem, employee, company = await meeting_for_test(return_all_objects=True)

        response = await client.delete(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem.id, meeting_id=meeting.id
            ),
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_no_meeting(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """
        Тест попытки удалить несуществующую встречу.
        """
        problem, employee, company = await problem_for_test(return_all_objects=True)
        meeting_id = random.randint(1, 100)

        response = await client.delete(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem.id, meeting_id=meeting_id
            ),
            headers=await get_token_for_user(employee),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            'detail': f'Не найден объект Meeting по данному id: {meeting_id}'
        }, response.json()
