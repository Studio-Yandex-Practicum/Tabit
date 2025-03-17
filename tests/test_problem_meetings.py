import random
import string
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import URL


def generate_meeting_data(
    problem_id, owner_id, all_fields=False, members=None, meeting_title=None, meeting_date=None
):
    """Генерирует реалистичные данные для создания встреч."""

    def random_string(length=10):
        """Генерирует случайную строку указанной длины."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    data = {
        'title': f'Встреча {random_string(5)}',
        'date_meeting': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'status': 'Новая',
        'problem_id': problem_id,
        'owner_id': str(owner_id),
    }
    if all_fields:
        data.update(
            {
                'description': f'Описание встречи {random_string(15)}',
                'place': f'Место встречи {random_string(6)}',
                'members': members,
            }
        )
    if meeting_title:
        data['title'] = meeting_title
    if meeting_date:
        data['date_meeting'] = meeting_date
    return data


class TestMeetingsPost:
    """
    Тесты post запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_create_meeting_whth_all_fields(
        self, client: AsyncClient, employee_of_company, problem_for_meeting, company_for_test
    ):
        """
        Тест пост запроса на создание встречи со всеми полями.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        members = [str((await employee_of_company()).id) for _ in range(3)]
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meeting_data = generate_meeting_data(
            all_fields=True, problem_id=problem_id, owner_id=owner.id, members=members
        )
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem_id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_201_CREATED
        response_data = response_meeting.json()
        assert response_data['title'] == meeting_data['title']
        assert response_data['date_meeting'] == meeting_data['date_meeting']
        assert response_data['status'] == meeting_data['status']

    @pytest.mark.asyncio
    async def test_create_meeting_with_required_fields(
        self, client: AsyncClient, employee_of_company, problem_for_meeting, company_for_test
    ):
        """
        Тест пост запроса на создание встречи только с обязательными полями.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meeting_data = generate_meeting_data(
            problem_id=problem_id,
            owner_id=owner.id,
        )
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem_id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_create_meeting_with_unique_name(
        self, client: AsyncClient, employee_of_company, problem_for_meeting, company_for_test
    ):
        """
        Тест пост запроса на проверку уникальности имени.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        fisrt_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        second_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meeting_title = 'Some Meeting'
        variants = (
            fisrt_date,
            second_date,
        )
        for date in variants:
            meeting_data = generate_meeting_data(
                problem_id=problem_id,
                owner_id=owner.id,
                meeting_date=date,
                meeting_title=meeting_title,
            )
            response_meeting = await client.post(
                URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem_id),
                json=meeting_data,
            )
        assert response_meeting.status_code == status.HTTP_400_BAD_REQUEST
        assert response_meeting.json() == {'detail': 'Такое название встречи уже используется'}

    @pytest.mark.asyncio
    async def test_create_meeting_with_uncurrent_date(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Тест пост запроса на создание встречи c не коректной датой.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        date_meeting = datetime.now() + timedelta(days=7)
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        await create_meeting(problem_id=problem_id, owner_id=owner.id, date=date_meeting)
        meeting_data = generate_meeting_data(
            problem_id=problem_id,
            owner_id=owner.id,
            meeting_date=date_meeting.strftime('%Y-%m-%d'),
        )
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem_id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_400_BAD_REQUEST
        assert response_meeting.json() == {'detail': 'Дата встречи уже занята'}

    @pytest.mark.asyncio
    async def test_create_no_company_no_problems(
        self, client: AsyncClient, employee_of_company, problem_for_meeting, company_for_test
    ):
        """
        Тест пост запроса на создание встречи c несуществующей компанией или проблемой.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        variants = (
            (
                problem_id,
                'No-way-company',
                status.HTTP_404_NOT_FOUND,
                {'detail': 'Такая компания не найдена'},
            ),
            (
                problem_id + 1,
                company.slug,
                status.HTTP_404_NOT_FOUND,
                {'detail': 'Такая проблема не найдена'},
            ),
        )
        for problem_id, company_slug, status_code, detail in variants:
            meeting_data = generate_meeting_data(
                problem_id=problem_id,
                owner_id=owner.id,
            )
            response_meeting = await client.post(
                URL.MEETINGS_ENDPOINT.format(company_slug=company_slug, problem_id=problem_id),
                json=meeting_data,
            )
            assert response_meeting.status_code == status_code, response_meeting.json()
            assert response_meeting.json() == detail


class TestMeetingsGet:
    """
    Тесты get запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_get_all_meetings_by_problem(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Проверка получения списка встреч по проблеме.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meetings_data = await create_meeting(
            problem_id=problem_id, owner_id=owner.id, count=3, data=True
        )
        meeting_data = meetings_data[0]
        response = await client.get(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem_id)
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 3
        for meting in response_data:
            assert meting['title'] == meeting_data['title']
            assert meting['date_meeting'] == meeting_data['date_meeting'].isoformat()
            assert meting['status'] == meeting_data['status']

    @pytest.mark.asyncio
    async def test_get_single_meeting_info(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Проверка получения информации о конкретной встрече.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meetings_data = await create_meeting(problem_id=problem_id, owner_id=owner.id, data=True)
        meeting_data = meetings_data[0]
        meeting_id = meeting_data['id']
        response = await client.get(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
            )
        )
        response_data = response.json()
        assert response_data['id'] == meeting_id
        assert response_data['title'] == meeting_data['title']
        assert response_data['date_meeting'] == meeting_data['date_meeting'].isoformat()
        assert response_data['status'] == meeting_data['status']

    @pytest.mark.asyncio
    async def test_get_meetings_standard_response(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Проверка корректного ответа на стандартный запрос если нет встреч.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        response = await client.get(
            URL.MEETINGS_ENDPOINT.format(company_slug=company.slug, problem_id=problem_id)
        )
        assert response.status_code == status.HTTP_200_OK
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
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Полное обновление всех полей встречи.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meetings_ids = await create_meeting(problem_id=problem_id, owner_id=owner.id)
        meeting_id = meetings_ids[0]
        updated_data = {
            'title': 'Updated Title',
            'date_meeting': (datetime.now() + timedelta(days=10)).date().isoformat(),
            'description': 'Updated Description',
            'status': 'Приостановлена',
            'place': 'Updated Place',
        }
        response = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
            ),
            json=updated_data,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for key, value in updated_data.items():
            assert data[key] == value

    @pytest.mark.asyncio
    async def test_patch_meeting_partial_update(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Обновление каждого поля встречи отдельно.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meetings_ids = await create_meeting(problem_id=problem_id, owner_id=owner.id)
        meeting_id = meetings_ids[0]
        variants = (
            ('title', 'Updated Title'),
            ('description', 'Updated Description'),
            ('date_meeting', (datetime.now() + timedelta(days=10)).date().isoformat()),
            ('status', 'Приостановлена'),
            ('place', 'Updated Place'),
        )
        for field, value in variants:
            response = await client.patch(
                URL.MEETINGS_SINGLE.format(
                    company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
                ),
                json={field: value},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data[field] == value

    @pytest.mark.asyncio
    async def test_update_meeting_not_found(self, client: AsyncClient, company_for_test):
        """
        Попытка обновить несуществующую встречу.
        """
        company = await company_for_test()
        problem_id = random.randint(0, 100)
        meeting_id = random.randint(0, 100)
        response_patch = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
            ),
            json={'title': 'No Matter'},
        )
        assert response_patch.status_code == status.HTTP_404_NOT_FOUND


class TestMeetingsDelete:
    """
    Тесты delete запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_delet_meeting(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Тест успешного удаления встречи.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meetings_ids = await create_meeting(problem_id=problem_id, owner_id=owner.id)
        meeting_id = meetings_ids[0]
        response = await client.delete(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delet_no_meeting(
        self,
        client: AsyncClient,
        employee_of_company,
        problem_for_meeting,
        company_for_test,
        create_meeting,
    ):
        """
        Тест попытки удалить несуществующую встречу.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await problem_for_meeting(company_id=company.id, owner_id=owner.id)
        meeting_id = 0

        response = await client.delete(
            URL.MEETINGS_SINGLE.format(
                company_slug=company.slug, problem_id=problem_id, meeting_id=meeting_id
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'Объект не найден'}
