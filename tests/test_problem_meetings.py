import random
import string
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import URL


def generate_meeting_data(problem_id, owner_id, all_fields=False, members=None):
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
    return data


class TestMeetingsPost:
    """
    Тесты post запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_create_meeting_whth_all_fields(
        self, client: AsyncClient, employee_of_company, problem_for_meeting
    ):
        """
        Тест пост запроса на создание встречи со всеми полями.
        """
        members = [str((await employee_of_company()).id) for _ in range(3)]
        problem = await problem_for_meeting()
        meeting_data = generate_meeting_data(
            all_fields=True, problem_id=problem.id, owner_id=problem.owner_id, members=members
        )
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=problem.company_slug, problem_id=problem.id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_201_CREATED
        response_data = response_meeting.json()
        assert response_data['description'] == meeting_data['description']
        assert response_data['place'] == meeting_data['place']

    @pytest.mark.asyncio
    async def test_create_meeting_with_required_fields(
        self, client: AsyncClient, problem_for_meeting
    ):
        """
        Тест пост запроса на создание встречи только с обязательными полями.
        """
        problem = await problem_for_meeting()
        meeting_data = generate_meeting_data(
            problem_id=problem.id,
            owner_id=problem.owner_id,
        )
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=problem.company_slug, problem_id=problem.id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_201_CREATED
        response_data = response_meeting.json()
        assert response_data['title'] == meeting_data['title']
        assert response_data['date_meeting'] == meeting_data['date_meeting']
        assert response_data['status'] == meeting_data['status']

    @pytest.mark.asyncio
    async def test_create_meeting_with_unique_name(
        self, client: AsyncClient, problem_for_meeting, create_meeting
    ):
        """
        Тест пост запроса на проверку уникальности имени.
        """
        problem = await problem_for_meeting()
        meeting = await create_meeting(
            problem_id=problem.id,
            owner_id=problem.owner_id,
        )
        new_date_meeting = (
            datetime.combine(meeting.date_meeting, datetime.min.time()) + timedelta(days=1)
        ).strftime('%Y-%m-%d')
        meeting_data = generate_meeting_data(
            problem_id=problem.id,
            owner_id=problem.owner_id,
        )
        meeting_data['title'] = meeting.title
        meeting_data['date_meeting'] = new_date_meeting
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=problem.company_slug, problem_id=problem.id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_400_BAD_REQUEST
        assert response_meeting.json() == {'detail': 'Такое название встречи уже используется'}

    @pytest.mark.asyncio
    async def test_create_meeting_with_uncurrent_date(
        self,
        client: AsyncClient,
        problem_for_meeting,
        create_meeting,
    ):
        """
        Тест пост запроса на создание встречи c не коректной датой.
        """
        problem = await problem_for_meeting()
        meeting = await create_meeting(problem_id=problem.id, owner_id=problem.owner_id)
        new_date_meeting = (datetime.combine(meeting.date_meeting, datetime.min.time())).strftime(
            '%Y-%m-%d'
        )
        meeting_data = generate_meeting_data(problem_id=problem.id, owner_id=problem.owner_id)
        meeting_data['date_meeting'] = new_date_meeting
        response_meeting = await client.post(
            URL.MEETINGS_ENDPOINT.format(company_slug=problem.company_slug, problem_id=problem.id),
            json=meeting_data,
        )
        assert response_meeting.status_code == status.HTTP_400_BAD_REQUEST
        assert response_meeting.json() == {'detail': 'Дата встречи уже занята'}

    @pytest.mark.asyncio
    async def test_create_no_company_no_problems(self, client: AsyncClient, problem_for_meeting):
        """
        Тест пост запроса на создание встречи c несуществующей компанией или проблемой.
        """
        problem = await problem_for_meeting()
        variants = (
            (
                problem.id,
                'No-way-company',
                status.HTTP_404_NOT_FOUND,
                {'detail': 'Такая компания не найдена'},
            ),
            (
                problem.id + 1,
                problem.company_slug,
                status.HTTP_404_NOT_FOUND,
                {'detail': 'Такая проблема не найдена'},
            ),
        )
        for problem_id, company_slug, status_code, detail in variants:
            meeting_data = generate_meeting_data(
                problem_id=problem_id,
                owner_id=problem.owner_id,
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
        problem_for_meeting,
        create_meeting,
    ):
        """
        Проверка получения списка встреч по проблеме.
        """
        problem = await problem_for_meeting()
        meetings_data = []
        for i in range(3):
            data = await create_meeting(problem_id=problem.id, owner_id=problem.owner_id, count=i)
            meetings_data.append(data)
        response = await client.get(
            URL.MEETINGS_ENDPOINT.format(company_slug=problem.company_slug, problem_id=problem.id)
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 3
        for i in range(3):
            assert response_data[i]['title'] == meetings_data[i].title
            assert response_data[i]['date_meeting'] == meetings_data[i].date_meeting.isoformat()
            assert response_data[i]['status'] == meetings_data[i].status

    @pytest.mark.asyncio
    async def test_get_single_meeting_info(
        self,
        client: AsyncClient,
        problem_for_meeting,
        create_meeting,
    ):
        """
        Проверка получения информации о конкретной встрече.
        """
        problem = await problem_for_meeting()
        meeting = await create_meeting(problem_id=problem.id, owner_id=problem.owner_id)
        response = await client.get(
            URL.MEETINGS_SINGLE.format(
                company_slug=problem.company_slug, problem_id=problem.id, meeting_id=meeting.id
            )
        )
        response_data = response.json()
        assert response_data['id'] == meeting.id
        assert response_data['title'] == meeting.title
        assert response_data['date_meeting'] == meeting.date_meeting.isoformat()
        assert response_data['status'] == meeting.status

    @pytest.mark.asyncio
    async def test_get_meetings_standard_response(
        self,
        client: AsyncClient,
        problem_for_meeting,
    ):
        """
        Проверка корректного ответа на стандартный запрос если нет встреч.
        """
        problem = await problem_for_meeting()
        response = await client.get(
            URL.MEETINGS_ENDPOINT.format(company_slug=problem.company_slug, problem_id=problem.id)
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
        problem_for_meeting,
        create_meeting,
    ):
        """
        Полное обновление всех полей встречи.
        """
        problem = await problem_for_meeting()
        meeting = await create_meeting(problem_id=problem.id, owner_id=problem.owner_id)
        updated_data = {
            'title': 'Updated Title',
            'date_meeting': (datetime.now() + timedelta(days=10)).date().isoformat(),
            'description': 'Updated Description',
            'status': 'Приостановлена',
            'place': 'Updated Place',
        }
        response = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=problem.company_slug, problem_id=problem.id, meeting_id=meeting.id
            ),
            json=updated_data,
        )
        assert response.status_code == status.HTTP_200_OK
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
        problem_for_meeting,
        create_meeting,
        field,
        value,
    ):
        """
        Обновление каждого поля встречи отдельно.
        """
        problem = await problem_for_meeting()
        meeting = await create_meeting(problem_id=problem.id, owner_id=problem.owner_id)

        response = await client.patch(
            URL.MEETINGS_SINGLE.format(
                company_slug=problem.company_slug, problem_id=problem.id, meeting_id=meeting.id
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
        assert response_patch.json() == {'detail': 'Такая проблема не найдена'}


class TestMeetingsDelete:
    """
    Тесты delete запросов к эндпоинту meetings.
    """

    @pytest.mark.asyncio
    async def test_delete_meeting(
        self,
        client: AsyncClient,
        problem_for_meeting,
        create_meeting,
    ):
        """
        Тест успешного удаления встречи.
        """
        problem = await problem_for_meeting()
        meeting = await create_meeting(problem_id=problem.id, owner_id=problem.owner_id)
        response = await client.delete(
            URL.MEETINGS_SINGLE.format(
                company_slug=problem.company_slug, problem_id=problem.id, meeting_id=meeting.id
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_no_meeting(
        self,
        client: AsyncClient,
        problem_for_meeting,
    ):
        """
        Тест попытки удалить несуществующую встречу.
        """
        problem = await problem_for_meeting()
        meeting_id = 0

        response = await client.delete(
            URL.MEETINGS_SINGLE.format(
                company_slug=problem.company_slug, problem_id=problem.id, meeting_id=meeting_id
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'Объект не найден'}
